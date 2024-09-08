from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import uuid4
from pydantic import BaseModel

class Country(Enum, str):
    Kenya = 'Kenya'
    Uganda = 'Uganda'
    Tanzania = 'Tanzania'
    Rwanda = 'Rwanda'
    Nigeria = 'Nigeria'
    Ghana = 'Ghana'
    South_Africa = 'South Africa'
    Angola = 'Angola'

class Company(Enum, str):
    Air_France = 'Air France'
    KLM = 'KLM'


class Contract(BaseModel):
    id: Optional[uuid4] = uuid4()
    name: str
    country: Country
    company: List[Company]
    category: str
    start_date: datetime
    end_date: datetime






