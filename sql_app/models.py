from ast import Bytes
from operator import index

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, DateTime, BINARY
from sqlalchemy.orm import relationship
from .database import Base



class User(Base):
    __tablename__ = 'users'

    id=Column(Integer, primary_key=True)
    email=Column(String(60), unique=True, index=True)
    username=Column(String(60), unique=True, index=True)
    hashed_password=Column(String(60))


#
# class Company(Base):
#     __tablename__ = 'companies'
#
#     id=Column(Integer, primary_key=True)
#     company_name=Column(String, index=True)
#     contracts= relationship('Contract', back_populates='company')

class Contract(Base):
    __tablename__ = 'contracts'

    id=Column(Integer, primary_key=True)
    contract_name=Column(String(100), index=True, unique=True)
    category=Column(String(100), index=True)
    start_date=Column(String(20), index=True)
    end_date=Column(String(20), index=True)
    country=Column(String(100), index=True)
    company_name=Column(String(20), index=True)
    vendor_name=Column(String(100), index=True)
    # status=Column(Boolean, index=True)
    status=Column(Integer, index=True)
    email_sent=Column(Integer, index=True)
    file_upload=Column(String(50))


class ExpiryEmail(Base):
    __tablename__ = 'expiry_emails'

    id=Column(Integer, primary_key=True)
    email=Column(String(60), index=True, unique=True)
































# from enum import Enum
# from typing import Optional, List
# from uuid import UUID, uuid4
#
# from pydantic import BaseModel
# from pydantic.v1 import root_validator
#
#
# class Country(str, Enum):
#     Kenya = 'Kenya'
#     Uganda = 'Uganda'
#     Tanzania = 'Tanzania'
#     Rwanda = 'Rwanda'
#     Nigeria = 'Nigeria'
#     Ghana = 'Ghana'
#     South_Africa = 'South Africa'
#     Angola = 'Angola'
#
# class Company(str, Enum):
#     AirFrance = 'Air France'
#     KLM = 'KLM'
#
#
# class Contract(BaseModel):
#     id: Optional[UUID] = uuid4()
#     name: str
#     country: Country
#     company: List[Company]
#     category: str
#     start_date: str
#     end_date: str
#
#
#     # @root_validator()
#     # def validate_dates(cls, values):
#     #     start = values.get('start_date')
#     #     end = values.get('end_date')
#     #     if start and end and start >= end:
#     #         raise ValueError(f'{start} should be be before {end}')
#     #     return values







