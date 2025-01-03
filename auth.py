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


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)














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