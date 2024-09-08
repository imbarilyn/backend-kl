from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel
from pydantic.v1 import root_validator


class Country(str, Enum):
    Kenya = 'Kenya'
    Uganda = 'Uganda'
    Tanzania = 'Tanzania'
    Rwanda = 'Rwanda'
    Nigeria = 'Nigeria'
    Ghana = 'Ghana'
    South_Africa = 'South Africa'
    Angola = 'Angola'

class Company(str, Enum):
    AirFrance = 'Air France'
    KLM = 'KLM'


class Contract(BaseModel):
    id: Optional[UUID] = uuid4()
    name: str
    country: Country
    company: List[Company]
    category: str
    start_date: str
    end_date: str


    # @root_validator()
    # def validate_dates(cls, values):
    #     start = values.get('start_date')
    #     end = values.get('end_date')
    #     if start and end and start >= end:
    #         raise ValueError(f'{start} should be be before {end}')
    #     return values







