import uuid
from sys import exc_info

from fastapi import APIRouter, Depends, Form
import pymysql
from pydantic import BaseModel

from app.dependencies import SessionDependency
import logging


router = APIRouter(
    prefix='/email',
    tags=['email']
)

class EmailAddress(BaseModel):
    email: str


def  check_email_length(db: pymysql.connections.Connection)-> int:
    with db.cursor() as cursor:
        try:
            query = """
            SELECT * FROM KlContract.expiry_emails
            """
            logging.info("Getting the length of the emails")
            cursor.execute(query)
            count = len(cursor.fetchall())
            print(f'Count: {count}')
            return count

        except Exception as e:
            logging.error(f'Error fetching emails: {e}', exc_info=True)
            # print(f'Error fetching emails: {e}')
            return -1
            # return None
def get_email(db: pymysql.connections.Connection, email: str):
    with db.cursor() as cursor:
        try:
            query = """
            SELECT * FROM KlContract.expiry_emails WHERE email = %s
            """
            cursor.execute(query, email)
            return cursor.fetchone()
        except Exception as e:
            print(f'Error fetching email: {e}')
            return None

def get_email_by_id(email_id: str, db: pymysql.connections.Connection):
    with db.cursor() as cursor:
        try:
            query = """
            SELECT * FROM KlContract.expiry_emails WHERE id = %s
            """
            cursor.execute(query, email_id)
            return cursor.fetchone()
        except Exception as e:
            print(f'Error fetching email: {e}')
            return None

@router.post('/add-emails')
def add_email(email_payload: EmailAddress, db: pymysql.connections.Connection = SessionDependency):
    print(f'Email: {email_payload}')
    db_email = get_email(db, email_payload.email)
    print(f'IF exists {db_email}')
    if db_email:
        return {'message': 'Email already exists', 'result': 'fail'}
    email_count = check_email_length(db)
    print (f'Email count--- {email_count}')
    if email_count == -1:
       return {
              'message': 'An error occurred, kindly try again',
              'result': 'fail'
       }
    if email_count >= 3:
        return {
            'message': 'Maximum number of emails reached, delete to add more',
            'result': 'fail'
        }
    email_id = uuid.uuid4()
    with db.cursor() as cursor:
        try:
            query = """
            INSERT INTO KlContract.expiry_emails (id, email)
            VALUES (%s, %s)
            """
            cursor.execute(query, (email_id, email_payload.email))
            db.commit()
            return {'message': 'Email added successfully', 'result': 'success'}
        except Exception as e:
            print(f'Error adding email: {e}')
            db.rollback()
            return {'message': 'Failed to add email', 'result': 'fail'}




@router.get('/get-emails')
def get_emails(db: pymysql.connections.Connection = SessionDependency):
    with db.cursor() as cursor:
        try:
            query = """
            SELECT * FROM KlContract.expiry_emails
            """
            cursor.execute(query)
            emails = cursor.fetchall()
            return {'result': 'success', 'emails': emails}
        except Exception as e:
            print(f'Error fetching emails: {e}')
            return {'result': 'fail', 'message': 'Could not access the data, please try again'}



@router.delete('/delete-email/{email_id}')
def delete_email(email_id: str, db: pymysql.connections.Connection = SessionDependency):
    db_email = get_email_by_id(email_id, db)
    if db_email is None:
        return {'message': 'Email not found', 'result': 'fail'}
    with db.cursor() as cursor:
        try:
            query = """
            DELETE FROM KlContract.expiry_emails WHERE id = %s
            """
            cursor.execute(query, email_id)
            db.commit()
            return {'message': 'Email deleted successfully', 'result': 'success'}
        except Exception as e:
            print(f'Error deleting email: {e}')
            db.rollback()
            return {'message': 'Failed to delete email', 'result': 'fail'}


@router.put('/update-email/{email_id}')
def update_email(email_id: str, email_payload: EmailAddress, db: pymysql.connections.Connection = SessionDependency):
    email_db = get_email_by_id(email_id, db)
    if email_db:
        with db.cursor() as cursor:
            try:
                query = """
                UPDATE KlContract.expiry_emails SET email = %s WHERE id = %s
                """
                cursor.execute(query, (email_payload.email, email_id))
                db.commit()
                return {'message': 'Email updated successfully', 'result': 'success'}
            except Exception as e:
                print(f'Error updating email: {e}')
                db.rollback()
                return {'message': 'Failed to update email', 'result': 'fail'}
    return {'message': 'Email not found', 'result': 'fail'}