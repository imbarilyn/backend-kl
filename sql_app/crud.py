from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import desc_op

from  .  import models, schemas
from fastapi.encoders import jsonable_encoder
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

def get_contracts(db: Session):
    # contracts = db.query(models.Contract).offset(skip).limit(limit).all()
    contracts = db.query(models.Contract).all()
    # print(contracts)
    # contracts_json = jsonable_encoder(contracts)
    if contracts:
        return {
            'result': 'success',
            'contracts': contracts
        }
        # return contracts
    return {
        'result': 'fail',
        'contracts':[]
    }



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
    if db_contract  is None:
        return {'message': 'Contract not created', 'result': 'fail'}
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return {'message': 'Contract created successfully', 'result': 'success'}

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
        db_contract.contract_name = contract.contract_name
        db_contract.category = contract.category
        db_contract.start_date = contract.start_date
        db_contract.end_date = contract.end_date
        db_contract.country = contract.country
        db_contract.vendor_name = contract.vendor_name
        db_contract.company_name = contract.company_name
        db_contract.status = contract.status
        db_contract.file_upload = contract.file_upload
        db.commit()
        return {'message': 'Contract updated successfully', 'result': 'success'}
    return {'message': 'Contract not found', 'result': 'fail'}

def max_email(db: Session):
    emails = db.query(models.ExpiryEmail).all()
    return len(emails) > 2



def get_email_by_name(db: Session, email: str):
    return db.query(models.ExpiryEmail).filter(models.ExpiryEmail.email == email).first()


def add_email(db: Session, email: schemas.ExpiryEmailBase):

    db_email = models.ExpiryEmail(email=email.email)

    if db_email is None:
        return {'message': 'Email not added', 'result': 'fail'}
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return {'message': 'Email added successfully', 'result': 'success'}

def get_emails(db: Session):
    emails = db.query(models.ExpiryEmail).order_by(desc_op(models.ExpiryEmail.id)).all()
    # emails = db.query(models.ExpiryEmail).all()
    if emails:
        email_list = [email for email in emails]
        return {'result': 'success', 'emails': email_list}
    return {'result': 'fail', 'emails': None}

def get_email(email_id: int, db: Session):
    email = db.query(models.ExpiryEmail).filter(models.ExpiryEmail.id == email_id).first()
    return email

def delete_email(email_id: int, db: Session):
    db_email = db.query(models.ExpiryEmail).filter(models.ExpiryEmail.id == email_id).first()
    if db_email is None:
        return {'message': 'Email not found', 'result': 'fail'}
    db.delete(db_email)
    db.commit()
    return {'message': 'Email deleted successfully', 'result': 'success'}

def update_email(email: schemas.ExpiryEmail, db: Session):
    db_email = db.query(models.ExpiryEmail).filter(models.ExpiryEmail.id == email.id).first()
    if db_email:
        db_email.email = email.email
        db.commit()
        return {'message': 'Email updated successfully', 'result': 'success'}
    return {'message': 'Email not found', 'result': 'fail'}





