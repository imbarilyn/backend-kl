from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from secrets import token_hex
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sql_app.schemas
from sql_app import models, schemas, crud, auth
from sql_app.database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pathlib import Path
from dotenv import load_dotenv
from sql_app.auth import get_current_active_user






models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(auth.router)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

if __name__ == '__main__':
# Mount upload directory as  static files
    app.mount("/uploads", StaticFiles(directory='uploads'), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins= ['http://localhost:5173'],
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
    db_contract = crud.get_contract_exists(db=db, contract_name=contract_name, company_name=company_name)
    if db_contract:
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
async def update_contract(contract_id: int,
                    contract_name: str = Form(...),
                    category: str = Form(...),
                    start_date: str = Form(...),
                    end_date: str = Form(...),
                    country: schemas.Country = Form(...),
                    vendor_name: str = Form(...),
                    company_name: schemas.Company = Form(...),
                    file: UploadFile = File(...),
                    db: Session = Depends(get_db)
                    ):
    required_ext = {'pdf'}
    # print(f"the contract is {contract}")
    db_contract = crud.get_contract(db, contract_id)
    if db_contract is None:
        # raise HTTPException(status_code=404, detail='Contract not found')
        return {'message': 'Contract not found', 'result': 'fail'}
    file_ext = file.filename.split('.').pop().lower()
    if file_ext not in required_ext:
        raise HTTPException(status_code=400, detail='Invalid file type')
    file_name = token_hex(10)
    file_path = os.path.join('uploads', f"{file_name}.{file_ext}")
    file_name_server = f"{file_name}.{file_ext}"
    print(f'file name {file_name_server}')
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)
    contract = models.Contract(
        id=contract_id,
        contract_name=contract_name,
        category=category,
        start_date=start_date,
        end_date=end_date,
        country=country,
        vendor_name=vendor_name,
        company_name=company_name,
        file_upload=file_name_server
    )
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


