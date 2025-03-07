from ast import Bytes
from operator import index

from google.protobuf.util.json_format_proto3_pb2 import EnumType
from sqlalchemy import Column, Integer, String, Enum, DateTime, BINARY
from sqlalchemy.orm import relationship
from .schemas import Status, EmailSent
from .database import Base



class User(Base):
    __tablename__ = 'users'

    id=Column(Integer, primary_key=True)
    email=Column(String(60), unique=True, index=True, nullable=False)
    username=Column(String(60), unique=True, index=True, nullable=False)
    hashed_password=Column(String(60))
    reset_token=Column(String(60), nullable=True)
    reset_token_expiry=Column(DateTime, nullable=True)
    used_reset_token=Column(Integer,  nullable=True)


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
    contract_name=Column(String(100))
    category=Column(String(100), index=True)
    start_date=Column(String(20), index=True)
    end_date=Column(String(20), index=True)
    country=Column(String(100), index=True)
    company_name=Column(String(20), index=True)
    vendor_name=Column(String(100), index=True)
    # status=Column(Boolean, index=True)
    status=Column(Enum(Status), index=True)
    email_sent=Column(Enum(EmailSent), index=True)
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







