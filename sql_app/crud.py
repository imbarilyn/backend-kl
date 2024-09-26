from sqlalchemy.orm import Session
from  .  import models, schemas
import bcrypt
# Get user by user_id
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip=0, limit=100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    # fake_hashed_password =bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    fake_hashed_password = user.password + 'neuro'
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_contract(db: Session, contract_id: int):
    db_contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    print(db_contract)
    return db_contract

def get_contract_by_name(db: Session, contract_name: str):
    print(f"in the crud {contract_name}")
    cont = db.query(models.Contract).filter(models.Contract.contract_name == contract_name).first()
    print(f"the contract is {cont}")
    return cont

def get_contracts(db: Session, skip: int=0, limit: int=100):
    return db.query(models.Contract).offset(skip).limit(limit).all()

def get_contract_by_country(db: Session, country: str):
    return db.query(models.Contract).filter(models.Contract.country == country).all()


def get_contract_by_company(db: Session, company: str):
    return db.query(models.Contract).filter(models.Contract.company_name == company).all()

def get_contract_by_category(db: Session, category: str):
    return db.query(models.Contract).filter(models.Contract.category == category).all()

def get_contract_by_status(db: Session, status: bool):
    return db.query(models.Contract).filter(models.Contract.status == status).all()

def get_contract_by_vendor(db: Session, vendor: str):
    return db.query(models.Contract).filter(models.Contract.vendor_name == vendor).all()

def create_contract(db: Session, contract: schemas.ContractCreate):
    print(f"we are now putting the contract in the db hooray{contract}")
    db_contract = models.Contract(**contract.model_dump())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

def delete_contract(db: Session, contract_id: int):
    db_contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if db_contract:
        db.delete(db_contract)
        db.commit()
        return {'message':  'Contract deleted successfully', 'result': 'success'}
    return {'message': 'Contract not found', 'result': 'fail'}

def update_contract(db: Session , contract: schemas.Contract):
    db_contract = db.query(models.Contract).filter(models.Contract.id == contract.id).first()
    if db_contract:
        for key, value in db_contract.dict().items():
            setattr(db_contract, key, value)
        db.commit()
        return {'message': 'Contract updated successfully', 'result': 'success'}
    return {'message': 'Contract not found', 'result': 'fail'}
