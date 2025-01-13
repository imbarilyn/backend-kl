import os
from os import close

from passlib.context import CryptContext
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing_extensions import deprecated

from sql_app import schemas, models
from jwt.exceptions import InvalidTokenError
from datetime import timedelta, datetime, timezone
from fastapi import Depends, status, HTTPException,APIRouter, Form, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sql_app.database import  SessionLocal, engine
from pathlib import Path
from dotenv import load_dotenv
from reset_password_mail import send_reset_password_mail
from secrets import token_urlsafe
from sqlalchemy import and_

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


current_dir = Path(__file__).resolve().parent if __file__ in locals() else Path.cwd()
env_directory = current_dir  / '.env'
load_dotenv(env_directory)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITH= os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES=30

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

# get_db dependency injection
# db_dependency= Session = Depends(get_db)

class Token(BaseModel):
    access_token: str
    token_type: str

class Users(BaseModel):
    username: str
    hashed_password: str

class ForgottenPassword(BaseModel):
    email: str
    username: str

# class ResetPassword(ForgottenPassword):
#     def __init__(self,
#                  username: str = Form(...),
#                     email: str = Form(...),
#                     password: str = Form(...),
#                  confirm_password: str = Form(...),
#                  token: str = Form(...)
#                  ):
#         super().__init__(username=username, email=email)
#         self.password = password
#         self.confirm_password = confirm_password
#         self.token = token

class ResetPassword(BaseModel):
    password: str
    confirm_password: str
    token: str


# custom OAuth2PasswordRequestForm to include email
class OAuth2PasswordRequestFormWithEmail(OAuth2PasswordRequestForm):
    def __init__(self,
                 username: str = Form(...),
                 password: str = Form(...),
                 email: str = Form(...)
                 ):
        super().__init__(username=username, password=password)
        self.email = email

def get_hashed_password(password: str):
    return bcrypt_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    print(bcrypt_context.verify(plain_password, hashed_password))
    return bcrypt_context.verify(plain_password, hashed_password)

def get_user(db: Session, username: str):
    # if username in db:
    #     user_dict = db['username']
    #     return schemas.UserCreate(**user_dict)
    return db.query(models.User).filter(models.User.username == username).first()



def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    print(f"user hashed password {user.hashed_password}")
    if not user:
        return  False
    if not verify_password(password, user.hashed_password):
        return  False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expires_in = datetime.now(timezone.utc) + expires_delta
    else:
        expires_in = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expires_in})
    jwt_encoded = jwt.encode(to_encode, SECRET_KEY, ALGORITH)
    return jwt_encoded

def get_current_active_user(token: str =  Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers = {'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITH)
        username: str = payload.get('sub')
        user_id: int = payload.get('user_id')
        exp: str = payload.get('exp')
        email: str = payload.get('email')
        if username is None or user_id is None:
            raise credential_exception
        return {'username': username, 'user_id': user_id, 'exp': exp, 'email': email}
    except InvalidTokenError:
        raise credential_exception

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
async def create_user( create_user_request: schemas.UserCreate, db: Session = Depends(get_db),):
    user_in_db = get_user(db, create_user_request.username)
    if user_in_db:
        raise HTTPException (
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username taken',
        )
    else:
        # create a user model instance
        create_user_model = models.User(
            username=create_user_request.username,
            email=create_user_request.email,
            hashed_password=get_hashed_password(create_user_request.password)
        )
        db.add(create_user_model)
        db.commit()
        return create_user_model

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestFormWithEmail = Depends(), db: Session=Depends(get_db)):
    print(f"form data {form_data.email}")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise  HTTPException (
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail='Wrong credentials',
            headers={"WWW-authorization": 'Bearer'}
        )
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username, "user_id": user.id, "email": user.email}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type='bearer')

def create_reset_token(user: schemas.User, db: Session):
    EXPIRY_DURATION = 24
    reset_token = token_urlsafe(32)
    token_expiry = datetime.now() + timedelta(hours=EXPIRY_DURATION)
    user.reset_token = reset_token
    user.reset_token_expiry = token_expiry
    user. used_reset_token = 0
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



@router.post('/forgotten-password', status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def forgot_password(forgot_password_request: ForgottenPassword, background_tasks: BackgroundTasks, db: Session=Depends(get_db)):
    user = get_user(db, forgot_password_request.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    updated_user = create_reset_token(user, db)
    if updated_user:
        send_reset_password_mail(background_tasks, user.email, user.username, updated_user.reset_token)
        return  updated_user

def validate_reset_password(token: str, db: Session):
   valid_user_reset = db.query(models.User).filter(
       and_(
       models.User.reset_token == token,
           models.User.used_reset_token == 0,
           models.User.reset_token_expiry > datetime.now()
   )
   ).first()
   if not valid_user_reset:
       return {
              'message': 'Invalid or expired token',
                'result': 'fail'
       }
   return valid_user_reset




@router.put('/reset-password', status_code=status.HTTP_200_OK, response_model=schemas.User)
def reset_password(
        password: str = Form(...),
        confirm_password: str = Form(...),
        token: str = Form(...),
        db:Session = Depends(get_db)):

    everything_valid = validate_reset_password(token, db)
    if everything_valid:
        match_password = confirm_password == password
        if not match_password:
            return {
                'message': 'Passwords do not match',
                'result': 'fail',
                'data': []
            }
        everything_valid.hashed_password = get_hashed_password(password)
        everything_valid.used_reset_token = 1
        everything_valid.reset_token = None
        everything_valid.reset_token_expiry = None
        db.add(everything_valid)
        db.commit()
        return {
            'message': 'Password reset successfully',
            'result': 'success',
            'data': everything_valid

        }























