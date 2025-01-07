from dotenv import load_dotenv
from fastapi import FastAPI, Depends, status, HTTPException, File, UploadFile, Form
from datetime import date, timedelta, timezone, datetime
from sqlalchemy.orm import Session
from secrets import token_hex
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sql_app.schemas
from sql_app import models, schemas, crud
from sql_app.database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from jwt.exceptions import  InvalidTokenError
from passlib.context import CryptContext
from pathlib import Path
from dotenv import load_dotenv
import auth
from auth import get_current_active_user


current_dir = Path(__file__).resolve().parent if '__file__' in locals() else Path.cwd()
env_directory = current_dir / '.env'
#
load_dotenv(env_directory)
SECRET_KEY=os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(auth.router)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

if __name__ == '__main__':
# Mount upload directory as  static files
    app.mount("/uploads", StaticFiles(directory='uploads'), name="uploads")

origins = [
    'http://localhost:5173'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# Dependency it is a
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
      # dependency for authentication
@app.get("/current-user")
async def user(current_user: dict = Depends(get_current_active_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    return {'user': user}

#
# # fake_users_db = {
# #     "johndoe": {
# #         "username": "johndoe",
# #         "full_name": "John Doe",
# #         "email": "johndoe@example.com",
# #         "hashed_password": "fakehashedsecret",
# #         "disabled": False,
# #     },
# #     "alice": {
# #         "username": "alice",
# #         "full_name": "Alice Wonderson",
# #         "email": "alice@example.com",
# #         "hashed_password": "fakehashedsecret2",
# #         "disabled": True,
# #     },
# # }
# fake_users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
#         "disabled": False,
#     }
# }
#
#
# @app.post('/users/', response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail='Email already exists')
#     return crud.create_user(db=db, user=user)
#

#
#
#
#
# # @app.get('/users/{user_id}', response_model=schemas.User)
# # def read_user(user_id: int, db: Session = Depends(get_db)):
# #     db_user = crud.get_user(db, user_id=user_id)
# #     if db_user is None:
# #         raise HTTPException(status_code=404, detail='User not found')
# #     return db_user
#
# # # Pydantic model in the token endpoint fro the response purpose
# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
# class TokenData(BaseModel):
#     username: str | None = None
#
#
# class User(BaseModel):
#     username: str
#     email: str | None = None
#     full_name: str | None = None
#     disabled: bool | None = None
#
#
# class UserInDB(User):
#     hashed_password: str
#
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
#
# def get_password_hash(password):
#     return pwd_context.hash(password)
#
# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         print(f"user in db {user_dict}")
#         # return UserInDB(**user_dict)
#         return User(**user_dict)
#
# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     print(f"user in db {user}")
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user
#
# # Utility function for generating new access token
# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
#
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail='Could not validate credentials',
#         headers={'WWW-Authenticate': 'Bearer'}
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username:  str = payload.get('sub')
#         if username is None:
#             raise credentials_exception
#         # instance of user created for safety purpose
#         token_data = TokenData(username=username)
#     except InvalidTokenError:
#         raise credentials_exception
#     user = get_user(fake_users_db, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user
#
#
# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user
#
# @app.post("/token")
# async def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),
# ) -> Token:
#     user = authenticate_user(fake_users_db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return Token(access_token=access_token, token_type="bearer")
#
# @app.get("/users/me")
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user
#
#
# def fake_hash_password(password: str):
#     return "fakehashed" + password
#
# def fake_decode_token(token):
#     # This doesn't provide any security at all
#     # Check the next version
#     print(f"the token is {token}")
#     user = get_user(fake_users_db, token)
#     return user
#
# @app.get("/users")
# async def read_me():
#     return {"msg": "Hello World"}

@app.post('/add-contracts')
async def create_contract(
        contract_name: str = Form(...),
        category: str = Form(...),
        start_date: str = Form(...),
        end_date: str = Form(...),
        country: schemas.Country = Form(...),
        vendor_name: str = Form(...),
        company_name: schemas.Company = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db),

):
    required_ext = {'pdf'}
    print(f"{contract_name}")
    db_contract = crud.get_contract_by_name(db=db, contract_name=contract_name)
    if db_contract:
        print(f"the contract exists {db_contract}")
        return {'message': 'Contract already exists', 'result': 'fail'}
        # raise HTTPException(status_code=400, detail='Contract already exists')

    if db_contract is None:
        print(f"The contract does not exist yet {db_contract}")
        file_ext = file.filename.split('.').pop().lower()
        print(f"{file_ext}")
        if file_ext not in required_ext:
            raise HTTPException(status_code=400, detail='Invalid file type')
        file_name = token_hex(10)

        # Ensure the uploads directory exists
        try:
            os.makedirs('uploads', exist_ok=True)
            file_path = os.path.join('uploads', f"{file_name}.{file_ext}")
            file_name_server = f"{file_name}.{file_ext}"
            # the  f is an object created once the file is open
            # we use 'wb' format tto write binary data to file for it may content images or pdfs
            with open(file_path, 'wb') as f:
                content = await file.read()
                f.write(content)
        except FileExistsError:
            raise HTTPException(status_code=400, detail='File already exists')

        contract_data = schemas.ContractCreate(
            contract_name=contract_name,
            category=category,
            start_date=start_date,
            end_date=end_date,
            country=country,
            vendor_name=vendor_name,
            company_name=company_name,
            file_upload=file_name_server
        )
        return crud.create_contract(db, contract=contract_data)


@app.get('/contract/{contract_id}')
def read_contract(contract_id: int, db: Session = Depends(get_db)):
    db_contract = crud.get_contract(db, contract_id)
    if db_contract is None:
        return {'message': 'Contract not found', 'result': 'fail'}
        # raise HTTPException(status_code=40, detail='Contract not found')

    return {'message': 'Contract found', 'result': 'success', 'data': db_contract}


@app.get('/uploads/{file_name}')
def read_file(file_name: str):
    print(f'Serving file: {file_name}')
    return FileResponse(f'uploads/{file_name}')


@app.get('/contracts/')
def get_contracts(db: Session = Depends(get_db), token: str = Depends(get_db)):
    db_contracts = crud.get_contracts(db)
    return db_contracts


@app.get('/expired-contracts')
def get_expired_contracts(db: Session = Depends(get_db)):
 expired_contracts = crud.expired_contracts(db)
 return expired_contracts


@app.delete('/delete-contract/{contract_id}')
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    db_contract = crud.get_contract(db, contract_id)
    print(db_contract)
    if db_contract is None:
        raise HTTPException(status_code=404, detail='Contract not found')
    return crud.delete_contract(db, contract_id)


@app.put('/update-contract/{contract_id}')
def update_contract(contract_id: int, contract: schemas.Contract, db: Session = Depends(get_db)):
    print(f"the contract is {contract}")
    db_contract = crud.get_contract(db, contract_id)
    if db_contract is None:
        # raise HTTPException(status_code=404, detail='Contract not found')
        return {'message': 'Contract not found', 'result': 'fail'}
    return crud.update_contract(db, contract)


@app.post('/add-emails')
def add_email(email: sql_app.schemas.ExpiryEmailBase, db: Session = Depends(get_db)):
    check_max = crud.max_email(db)
    if check_max:
        return {'message': 'Maximum number of emails reached', 'result': 'fail'}
    db_email = crud.get_email_by_name(db, email.email)
    print(f'{db_email}')
    if db_email:
        return {'message': 'Email already exists', 'result': 'fail'}
    return crud.add_email(db, email)


@app.get('/emails/')
def get_emails(db: Session = Depends(get_db)):
    emails = crud.get_emails(db)
    print(emails)
    return emails


@app.delete('/delete-email/{email_id}')
def delete_email(email_id: int, db: Session = Depends(get_db)):
    db_email = crud.get_email(email_id, db)
    if db_email is None:
        return {'message': 'Email not found', 'result': 'fail'}
    return crud.delete_email(email_id, db)


@app.put('/update-email/{email_id}')
def update_email(email_id: int, email: sql_app.schemas.ExpiryEmail, db: Session = Depends(get_db)):
    email_db = crud.get_email(email_id, db)
    print(f"Email--: {email}")
    if email_db:
        print(f'{email_db}')
        return crud.update_email(email, db)
    return {'message': 'Email not found', 'result': 'fail'}


