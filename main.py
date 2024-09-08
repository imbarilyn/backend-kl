from typing import List
from uuid import uuid4, UUID
from uuid import uuid4
from fastapi import FastAPI
from pydantic.v1 import UUID1

from models import Country, Company, Contract

app = FastAPI()
db: List[Contract] = [
    Contract(
        id= UUID('7e7584d9-9af5-41cd-8876-3abe528cc600'),
        name='Contract 1',
        country=Country.Kenya,
        company=[Company.AirFrance],
        category='Category 1',
        start_date='2021-01-01',
        end_date='2021-12-31'
    ),
    Contract(
        id= UUID('dbf0688d-9b6a-4af2-8d11-a5f2befecfcc'),
        name='Contract 2',
        country=Country.Uganda,
        company=[Company.KLM],
        category='Category 2',
        start_date='2021-01-01',
        end_date='2021-12-31'
    ),
    Contract(
        id= UUID('befef56e-6386-4953-8d90-ebad59614016'),
        name='Contract 3',
        country=Country.Tanzania,
        company=[Company.AirFrance, Company.KLM],
        category='Category 3',
        start_date='2021-01-01',
        end_date='2021-12-31'
    ),
    Contract(
        id= UUID('37bef92f-42df-4c94-834f-2fb71eb3a2eb'),
        name='Contract 4',
        country=Country.Tanzania,
        company=[Company.AirFrance],
        category='Category 3',
        start_date='2021-01-01',
        end_date='2021-12-31'
    ),
]


@app.get('/contracts/')
async def get_contracts():
    return db
@app.post('/create-contract/')
async def create_contract(contract: Contract):
    if contract:
        return { 'contract': contract}
    return {'result': 'fail', 'message': 'Could not create contract'}

@app.get('/contracts-country/{country}')
async def get_contracts_by_country(country: Country):
    contracts = [contract for contract in db if contract.country == country]
    if not contracts:
        return {'result': 'fail', 'message': 'Contracts not found'}
    return contracts

@app.get('/contracts-company/{company}')
async def get_contracts_by_company(company: Company):
    contracts =  [contract for contract in db if company in contract.company]
    if not contracts:
        return {'result': 'fail', 'message': 'Contracts not found'}
    return contracts

@app.patch('/update-contract/{contract_id}')
async def update_contract(contract_id: UUID, contract: Contract ):
    for cont in db:
        if cont.id == contract_id:
            cont.name = contract.name
            cont.country = contract.country
            cont.company = contract.company
            cont.category = contract.category
            cont.start_date = contract.start_date
            cont.end_date = contract.end_date
            return {'result': 'success', 'message': 'Contract updated'}
        return {'result': 'fail', 'message': 'Contract not found'}

@app.get('/contracts-category/{category}')
async def get_contract_by_category(category: str):
   contracts =  [contract for contract in db if contract.category == category]
   if not contracts:
       return {'result': 'fail', 'message': 'Contracts not found'}
   return contracts

@app.get('/contracts-start-date/{start_date}')
async def get_contract_by_date(start_date: str):
    contracts = [contract for contract in db if contract.start_date == start_date]
    if not contracts:
        return {'result': 'fail', 'message': 'Contracts not found'}
    return contracts

@app.get('/contracts-end-date/{end_date}')
async def get_contract_by_date(end_date: str):
    contracts = [contract for contract in db if contract.end_date == end_date]
    if not contracts:
        return {'result': 'fail', 'message': 'Contracts not found'}
    return contracts

@app.get('/contract-name/{name}')
async def get_contract_by_name(name: str):
    for contract in db:
        if contract.name == name:
            return [contract]
        return {'result': 'fail', 'message': 'Contract not found'}
