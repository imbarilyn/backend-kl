import os
from os import close

from passlib.context import CryptContext
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing_extensions import deprecated

from sql_app import schemas, models
from jwt.exceptions import InvalidTokenError
from datetime import timedelta, datetime
from fastapi import Depends, status, HTTPException,APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sql_app.database import  SessionLocal, engine
from pathlib import Path


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





# models.Base.metadata.create_all(bind=engine)
#
# oauth2_scheme=OAuth2PasswordBearer(tokenUrl='token')
# pwd_context=CryptContext(schemes=['bcrypt'], deprecated='auto')
#
#
# def get_db():
#     db=SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# app=FastAPI()
#
# @app.post("/token")
# async  def