from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from datetime import date
from sqlalchemy.orm  import Session
from secrets import token_hex

from  sql_app import models, schemas, crud
from  sql_app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/users/', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session=Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail='Email already exists')
    return crud.create_user(db=db, user=user)

@app.get('/users/{user_id}', response_model=schemas.User)
def read_user(user_id: int, db: Session=Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return db_user

@app.post('/contracts', response_model=schemas.Contract)
async def create_contract(
        contract_name: str=Form(...),
        category: str=Form(...),
        start_date: date=Form(...),
        end_date: date=Form(...),
        country: schemas.Country=Form(...),
        vendor_name: str=Form(...),
        company_name: schemas.Company=Form(...),
        expired_status: bool=Form(...),
        file: UploadFile=File(...),
        db: Session=Depends(get_db)):
    required_ext = {'pdf', 'doc', 'docx'}
    print(f"{contract_name}")
    db_contract = crud.get_contract_by_name(db=db, contract_name = contract_name)
    if db_contract:
        print(f"the contract exists {db_contract}")
        raise HTTPException(status_code=400, detail='Contract already exists')
    if db_contract is None:
        print(f"The contract does not exist yet {db_contract}")
        file_ext = file.filename.split('.').pop().lower()
        print(f"{file_ext}")
        if file_ext not in required_ext:
            raise HTTPException(status_code=400, detail='Invalid file type')
        file_name = token_hex(20)

        # Ensure the uploads directory exists
        try:
            os.makedirs('uploads', exist_ok=True)
            file_path = os.path.join('uploads', f"{file_name}. {file_ext}")
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
            expired_status=expired_status,
            file_upload=file_path
        )
        return crud.create_contract(db, contract=contract_data)

@app.get('/contracts/{contract_id}', response_model=schemas.Contract)
def read_contract(contract_id: int, db: Session=Depends(get_db)):
    db_contract = crud.get_contract(db, contract_id)
    if db_contract is None:
        raise HTTPException(status_code=40, detail='Contract not found')
    return db_contract

@app.get('/contracts/', response_model=list[schemas.Contract])
def get_contracts(db: Session=Depends(get_db), skip: int=0, limit: int=100):
    db_contracts = crud.get_contracts(db, skip=skip, limit=limit)
    return db_contracts

@app.delete('/contracts/{contract_id}')
def delete_contract(contract_id: int, db: Session=Depends(get_db)):
    db_contract = crud.get_contract(db, contract_id)
    print(db_contract)
    if db_contract is None:
        raise HTTPException(status_code=404, detail='Contract not found')
    return crud.delete_contract(db, contract_id)

@app.put('/contracts/{contract_id}', response_model=schemas.Contract)
def update_contract(contract_id: int, contract: schemas.Contract, db: Session=Depends(get_db)):
    db_contract = crud.get_contract(db, contract_id)
    if db_contract is None:
        raise HTTPException(status_code=404, detail='Contract not found')
    return crud.update_contract(db, contract)
