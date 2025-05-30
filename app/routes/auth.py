import os
from datetime import datetime, timezone
from pathlib import Path
import jwt
import pymysql.connections
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form, status, HTTPException
from datetime import timedelta
from jwt import InvalidTokenError
from sqlmodel import SQLModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.routes.reset_pasword_email import send_reset_email
from app.dependencies import SessionDependency
import uuid


class Token(SQLModel):
    access_token: str
    token_type: str

class ForgottenPassword(SQLModel):
    email: str

class OAuth2PasswordRequestFormCustom(OAuth2PasswordRequestForm):
    def __init__(self, email: str = Form(...),
                 password: str = Form(...)
                 ):
        super().__init__(username=email, password=password)


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')
ACCESS_TOKEN_EXPIRY = 7
current_dir = Path(__file__).resolve().parent if __file__ in locals() else Path.cwd()
env_directory = current_dir / '.env'
load_dotenv(env_directory)


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM= os.getenv('ALGORITHM')

router = APIRouter(
    prefix="/auth",
    tags=['auth-aggregator']
)

def user_in_db(email: str, db: pymysql.connections.Connection):
    with db.cursor() as cursor:
        try:
            query = """
            SELECT *  FROM KlContract.users WHERE email = %s
            """
            cursor.execute(query, email)
            return  cursor.fetchone()
        except Exception as e:
            print(f'Error fetching user: {e}')
            return None

def get_hashed_password(password: str):
    return bcrypt_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expires_in = datetime.now(timezone.utc) + expires_delta
    else:
        expires_in = datetime.now(timezone.utc) + timedelta(days = 7)
    to_encode.update({"exp": expires_in})
    jwt_encoded = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return jwt_encoded

def get_current_active_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        exp: str = payload.get('exp')
        user_id = payload.get('user_id')
        if email or user_id is None:
            raise credentials_exception
        return {'email': email, 'user_id': user_id, 'exp': exp}
    except InvalidTokenError:
        raise credentials_exception

@router.post('/create')
async def create_user(
        email: str = Form(...),
        username: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        db: pymysql.connections.Connection = SessionDependency
):
    user = user_in_db(email, db)
    if user:
        return {
            'message': 'User already exists',
            'result': 'fail'
        }
    else:
        if password != confirm_password:
            return {
                'message': 'Passwords do not match',
                'result': 'fail'
            }

        hashed_password = get_hashed_password(password)
        user_id = str(uuid.uuid4())
        with db.cursor() as cursor:
            try:
                query = """
                INSERT INTO users (id, email, username,  hash_password) VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (user_id, email, username, hashed_password))
                db.commit()
                return {
                    'message': 'User created successfully',
                    'result': 'success'
                }
            except Exception as e:
                print(f'Error creating user: {e}')
                db.rollback()
                return {
                    'message': 'Failed to create user',
                    'result': 'fail'
                }


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestFormCustom = Depends(), db: pymysql.connections.Connection = SessionDependency):
    print("We are here on the login page---")
    user = user_in_db(form_data.username, db)
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    if not user or not verify_password(form_data.password, user['hash_password']):
        raise credential_exception
    access_token_expiry = timedelta(days=ACCESS_TOKEN_EXPIRY)
    access_token = create_access_token(data={'sub': user['email'], 'username': user['username'], 'user_id': user['id']}, expires_delta=access_token_expiry)
    return Token(access_token=access_token, token_type='bearer')


@router.post('/forgot-password')
async def forgot_password(email: str = Form(...), db: pymysql.connections.Connection = SessionDependency):
    user = user_in_db(email, db)
    if not user:
        return {
            'message': 'User does not exist',
            'result': 'fail'
        }
    else:
        reset_token = str(uuid.uuid4())
        reset_token_expiry = datetime.now() + timedelta(hours=24)
        with db.cursor() as cursor:
            try:
                query = """
                INSERT INTO password_reset (id, user_id, reset_token, reset_token_expiry, used_reset_token)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (str(uuid.uuid4()), user['id'], reset_token, reset_token_expiry, 'no'))
                db.commit()
                email_sent = send_reset_email(user['username'], user['email'], reset_token, db)
                if email_sent:
                    return {
                        'message': 'Kindly check your email to reset password',
                        'result': 'success'
                    }
                else:
                    return {
                        'message': 'Failed to send reset token',
                        'result': 'fail'
                    }
            except Exception as e:
                print(f'Error sending reset token: {e}')
                db.rollback()
                return {
                    'message': 'Failed to send reset token',
                    'result': 'fail'
                }


@router.post('/reset-password')
async def reset_password(
        reset_token: str =Form(...),
        new_password: str = Form(...),
        confirm_password: str = Form(...),
        db: pymysql.connections.Connection = SessionDependency):
    print(f'reset token: {reset_token}')
    with db.cursor() as cursor:
        try:
            query = """
            SELECT * FROM password_reset WHERE reset_token = %s
            """
            cursor.execute(query, reset_token)
            reset_data = cursor.fetchone()
            print(f'reset data: {reset_data}')
            if not reset_data or reset_data['reset_token_expiry'] < datetime.now():
                return {
                    'message': 'Invalid reset token, please try again',
                    'result': 'fail'
                }
            if reset_data['used_reset_token'] == 'yes':
                return {
                    'message': 'Reset token already used',
                    'result': 'fail'
                }
            if new_password != confirm_password:
                return {
                    'message': 'Passwords do not match',
                    'result': 'fail'
                }
            hashed_password = get_hashed_password(new_password)
            query = """
            UPDATE users SET hash_password = %s WHERE id = %s
            """
            cursor.execute(query, (hashed_password, reset_data['user_id']))
            query = """
            UPDATE password_reset SET used_reset_token = 'yes' WHERE id = %s
            """
            cursor.execute(query, reset_data['id'])
            db.commit()
            return {
                'message': 'Password reset successfully',
                'result': 'success'
            }
        except Exception as e:
            print(f'Error resetting password: {e}')
            db.rollback()
            return {
                'message': 'Failed to reset password',
                'result': 'fail'
            }






