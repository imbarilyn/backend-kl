from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field


class Country(str, Enum):
    kenya='Kenya'
    uganda='Uganda'
    tanzania='Tanzania'
    rwanda='Rwanda'
    ghana='Ghana'
    south_africa='South Africa'
    zambia='Zambia'
    burundi='Burundi'
    malawi='Malawi'
    ethiopia='Ethiopia'
    sudan='Sudan'


class Company(str, Enum):
    af='Air France'
    klm='KLM'

class Status(int, Enum):
    active = 1
    expired = 0

class EmailSent(int, Enum):
    yes = 1
    no = 0

class ContractBase(BaseModel):
    contract_name: str
    category: str
    start_date: str
    end_date: str
    country: Country
    vendor_name: str
    company_name: Company
    status: Status
    file_upload: str
    email_sent: EmailSent



class ContractCreate(ContractBase):
    pass

class Contract(ContractBase):
    id: int

    class Config:
        orm_mode = True




class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    email:str

    class Config:
        orm_mode = True


class ExpiryEmailBase(BaseModel):
    email: str

class ExpiryEmailCreate(ExpiryEmailBase):
    pass

class ExpiryEmail(ExpiryEmailBase):
    id: int


    class Config:
        orm_mode = True
