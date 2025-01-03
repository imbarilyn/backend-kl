import os
from os import close

from passlib.context import CryptContext
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing_extensions import deprecated

from main import current_dir, env_directory, SECRET_KEY
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
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITH='HS256'
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')












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