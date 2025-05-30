import os
import uuid
from datetime import datetime, timedelta
from re import search
from typing import List, Optional

import pymysql
from pydantic import BaseModel

from app import schemas
from secrets import token_hex
from fastapi.responses import FileResponse
from app.dependencies import SessionDependency
from fastapi import APIRouter, Request, Form, UploadFile, File

router = APIRouter(
    prefix='/contracts',
    tags=['contracts']
)
# class DataTablesResponse(BaseModel):
#     data: List[ContractBase]
#     recordsTotal: int
#     recordsFiltered: int


def get_contract_by_name(contract_name: str, company_name: schemas.Company, db: pymysql.connections.Connection):
    with db.cursor() as cursor:
        try:
            query = """
            SELECT * FROM KlContract.contracts WHERE contract_name = %s AND company_name = %s
            """
            cursor.execute(query, (contract_name, company_name))
            return cursor.fetchone()
        except Exception as e:
            print(f'Error fetching contract: {e}')
            return None


def add_contract(contract_name: str, category: str, start_date: datetime, end_date: datetime, country: schemas.Country,
                 vendor_name: str, company_name: schemas.Company, file_upload: str, db: pymysql.connections.Connection):
    contract_id = uuid.uuid4()
    with db.cursor() as cursor:
        try:
            query = """
            INSERT INTO KlContract.contracts (id, contract_name, category, start_date, end_date, country, vendor_name, company_name, file_upload, status, email_sent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (contract_id, contract_name, category, start_date, end_date, country, vendor_name, company_name, file_upload, 'active', 'no'))
            db.commit()
            return True
        except Exception as e:
            print(f'Error adding contract: {e}')
            db.rollback()
            return False


def get_contract_by_id(contract_id: str, db: pymysql.connections.Connection):
    with db.cursor() as cursor:
        try:
            query = """
            SELECT * FROM KlContract.contracts WHERE id = %s
            """
            cursor.execute(query, contract_id)
            return cursor.fetchone()
        except Exception as e:
            print(f'Error fetching contract: {e}')
            return None

def get_all_contracts(db: pymysql.connections.Connection):
    with db.cursor() as cursor:
        try:
            query = """
               SELECT * FROM KlContract.contracts
               """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f'Error fetching contracts: {e}')
            return None

def expired_contracts(db: pymysql.connections.Connection):

    with db.cursor() as cursor:
        try:
            query = """
            SELECT * FROM KlContract.contracts WHERE  status = 'expired'
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f'Error fetching expired contracts: {e}')
            return None
def set_contract(
        contract_id: str,
        contract_name: str,
        category: str,
        start_date: datetime,
        end_date: datetime,
        country: schemas.Country,
        vendor_name: str,
        company_name: schemas.Company,
        file_upload: str,
        db: pymysql.connections.Connection
):
    threshold = datetime.now() + timedelta(days=30)
    with db.cursor() as cursor:
        try:
            query = """
            UPDATE KlContract.contracts SET contract_name = %s, category = %s, start_date = %s, end_date = %s, country = %s, vendor_name = %s, company_name = %s, file_upload = %s, status = %s, email_sent = %s WHERE id = %s
            """
            if end_date > threshold:
                print(f" Editing contract--- {end_date > threshold}")
                cursor.execute(query, (contract_name, category, start_date, end_date, country, vendor_name, company_name, file_upload, 'active', 'no', contract_id))
            else:
                cursor.execute(query, (contract_name, category, start_date, end_date, country, vendor_name, company_name, file_upload, 'expired', 'yes', contract_id))
            db.commit()
            return True
        except Exception as e:
            print(f'Error updating contract: {e}')
            db.rollback()
            return False


@router.post('/add-contracts')
async def create_contract(
        contract_name: str = Form(...),
        category: str = Form(...),
        start_date: datetime = Form(...),
        end_date: datetime = Form(...),
        country: schemas.Country = Form(...),
        vendor_name: str = Form(...),
        company_name: schemas.Company = Form(...),
        file: UploadFile = File(...),
        db: pymysql.connections.Connection = SessionDependency
):
    required_ext = {'pdf'}
    contract = get_contract_by_name(contract_name, company_name, db)
    if contract:
        return {'message': 'Contract already exists', 'result': 'fail'}
    file_ext = file.filename.split('.').pop().lower()
    print(f"{file_ext}")
    if file_ext not in required_ext:
         return {'message': 'Invalid file type', 'result': 'fail'}
    file_name = token_hex(10)

    # Ensure the uploads directory exists
    try:
        os.makedirs('uploads', exist_ok=True)
        file_path = os.path.join('uploads', f"{file_name}.{file_ext}")
        file_name_server = f"{file_name}.{file_ext}"
        # the  f is an object created once the file is open
        # we use 'wb' format tto write binary data to file for it may content images or pdfs
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
    except FileExistsError:
        # raise HTTPException(status_code=400, detail='File already exists')
        return {'message': 'File already exists', 'result': 'fail'}

    contract_data = add_contract(
            contract_name,
            category,
            start_date,
            end_date,
            country,
            vendor_name,
            company_name,
            file_name_server,
        db
    )
    if contract_data:
        return {'message': 'Contract added successfully', 'result': 'success'}
    return {'message': 'Failed to add contract', 'result': 'fail'}


@router.get('/contract/{contract_id}')
def read_contract(contract_id: str, db: pymysql.connections.Connection = SessionDependency):
    db_contract = get_contract_by_id(contract_id, db)
    if db_contract is None:
        return {'message': 'Contract not found', 'result': 'fail', 'data': []}
    return {'message': 'Contract found', 'result': 'success', 'data': db_contract}


@router.get('/uploads/{file_name}')
def read_file(file_name: str):
    print(f'Serving file: {file_name}')
    return FileResponse(f'uploads/{file_name}')

# def get_all_contract_server_side(start: Optional[int] = None, length: Optional[int] = None, search_value: Optional[str] = None, order_dir: Optional[str] = None, order_column: Optional[int] = None, db: pymysql.connections.Connection = SessionDependency):
#     with db.cursor() as cursor:
#         try:
#             query = """
#             SELECT * FROM KlContract.contracts
#             """
        # try:
        #     query = """
        #     SELECT * FROM KlContract.contracts
        #     """
        #     cursor.execute(query)
        #     contracts = cursor.fetchall()
        #     if search_value:
        #         contracts = [contract for contract in contracts if search_value in contract]
        #     if order_dir and order_column:
        #         contracts = sorted(contracts, key=lambda x: x[order_column], reverse=order_dir == 'desc')
        #     if start and length:
        #         contracts = contracts[start:start + length]
        #     return {'data': contracts, 'recordsTotal': len(contracts), 'recordsFiltered': len(contracts)}
        # except Exception as e:
        #     print(f'Error fetching contracts: {e}')
        #     return None

@router.get('/view-contracts')
async def get_contracts(
#     request: Request,
#     start: Optional[int] = Query(None),
#     length: Optional[int] = Query(None),
#     search_value: Optional[str] = Query(None, alias="search[value]"),
#     order_dir: Optional[str] = Query(None, alias="order[0][dir]"),
#     order_column: Optional[int] = Query(None, alias="order[0][column]"),
#     draw: int = Query(0)
# ):
#
#     req_body = await request.body()
#     # logging.info(req_body)
#     contracts = get_all_contract_server_side(start, length, search_value,order_dir, order_colum)
#     return {**contracts, "draw": draw}
    db: pymysql.connections.Connection = SessionDependency
):


   contracts = get_all_contracts(db)

   print(f'Contracts: {contracts}')
   if contracts is None:
       return {'result': 'fail', 'data': []}
   total = len(contracts)
   return {'result': 'success', 'data': contracts, 'total': total}


@router.get('/expired-contracts')
def get_expired_contracts(db: pymysql.connections.Connection = SessionDependency):
    expired = expired_contracts(db)
    total = len(expired)
    if expired is None:
        return {'result': 'fail', 'data': []}
    return {'result': 'success', 'data': expired, 'total': total}


@router.delete('/delete-contract/{contract_id}')
def delete_contract(contract_id: str, db: pymysql.connections.Connection = SessionDependency):
    db_contract = get_contract_by_id(contract_id, db)
    if db_contract is None:
        return {'message': 'Contract not found', 'result': 'fail'}
    with db.cursor() as cursor:
        try:
            query = """
            DELETE FROM KlContract.contracts WHERE id = %s
            """
            cursor.execute(query, contract_id)
            db.commit()
            return {'message': 'Contract deleted successfully', 'result': 'success'}
        except Exception as e:
            print(f'Error deleting contract: {e}')
            db.rollback()
            return {'message': 'Failed to delete contract', 'result': 'fail'}


@router.put('/update-contract/{contract_id}')
async def update_contract(contract_id: str,
                    contract_name: str = Form(...),
                    category: str = Form(...),
                    start_date: datetime = Form(...),
                    end_date: datetime = Form(...),
                    country: schemas.Country = Form(...),
                    vendor_name: str = Form(...),
                    company_name: schemas.Company = Form(...),
                    file: UploadFile = File(...),
                    db: pymysql.connections.Connection = SessionDependency
                    ):
    required_ext = {'pdf'}
    db_contract = get_contract_by_id(contract_id, db)
    if db_contract is None:
        return {'message': 'Contract not found', 'result': 'fail'}
    file_ext = file.filename.split('.').pop().lower()
    if file_ext not in required_ext:
        # raise HTTPException(status_code=400, detail='Invalid file type')
        return {'message': 'Invalid file type only pdf', 'result': 'fail'}
    file_name = token_hex(10)
    file_path = os.path.join('uploads', f"{file_name}.{file_ext}")
    file_name_server = f"{file_name}.{file_ext}"
    print(f'file name {file_name_server}')
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)
    contract = set_contract(
        contract_id,
        contract_name,
        category,
        start_date,
        end_date,
        country,
        vendor_name,
        company_name,
        file_name_server,
        db
    )
    if contract:
        return {'message': 'Contract updated successfully', 'result': 'success'}
    return {'message': 'Failed to update contract', 'result': 'fail'}



