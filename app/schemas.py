from datetime import datetime, date
from email.policy import default
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

from sqlmodel import SQLModel


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
    angola='Angola'


class Company(str, Enum):
    af='Air France'
    klm='KLM'
#
# class Status(int, Enum):
#     active = 'active'
#     expired = 'expired'
#
# class EmailSent(int, Enum):
#     yes = 'yes'
#     no = 'no'
#
# class UsedToken(int, Enum):
#     yes = 1
#     no = 0
# #
# class ContractBase(SQLModel):
#     contract_name: str
#     category: str
#     start_date: str
#     end_date: str
#     country: Country
#     vendor_name: str
#     company_name: Company
#     status: Status
#     file_upload: str
#     email_sent: EmailSent
#
#
#
# class ContractCreate(ContractBase):
#     status: Status = Field(default = Status.active, description="Whether it is expired or active")
#     email_sent: EmailSent = Field(default = EmailSent.no, description="Whether the email notification for expiration has been sent or not")
#
# class Contract(ContractBase):
#     id: int
#
#     class Config:
#         from_attributes = True
#
#
#
#
# class UserBase(BaseModel):
#     email: str
#     username: str
#
#
# class UserCreate(UserBase):
#     password: str
#
# class User(UserBase):
#     id: int
#     hashed_password: str
#     reset_token_expiry: Optional[datetime] = None
#     reset_token: Optional[str] = None
#     used_reset_token: Optional[int] = UsedToken.no.value
#     # linah.imbari@student.moringaschool.com
#
#     class Config:
#         from_attributes = True
#
#
# class ExpiryEmailBase(BaseModel):
#     email: str
#
# class ExpiryEmailCreate(ExpiryEmailBase):
#     email: str
#
# class ExpiryEmail(ExpiryEmailBase):
#     id: int
#
#     class Config:
#         from_attributes = True
