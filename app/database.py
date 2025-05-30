import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os
from pathlib import Path
from contextlib import closing


current_directory = Path(__file__).resolve().parent if __file__ in locals() else Path.cwd()
env_file = current_directory / '.env'
load_dotenv(env_file)

user = os.getenv('DB_USER_LOCAL')
localhost = os.getenv('DB_HOST')
password= os.getenv('DB_PASSWORD')
database= os.getenv('DB_DATABASE')

isServer = False
# isServer = True
if not isServer:
    DB_CONFIG = {
        "host": localhost,
        "user": 'root',
        "password": password,
        "database": database,
        "cursorclass": DictCursor
    }
else:
    DB_CONFIG = {
        "host": localhost,
        "user": user,
        "password": password,
        "database": database,
        "cursorclass": DictCursor
    }

def get_db():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        yield connection
    finally:
        connection.close()

queries = [
    """
    CREATE TABLE IF NOT EXISTS users(
        id CHAR(36) PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        hash_password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS  contracts(
        id CHAR(36) PRIMARY KEY,
        contract_name VARCHAR(255) NOT NULL,
        category VARCHAR(255) NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        country VARCHAR(255) NOT NULL,
        company_name VARCHAR(255) NOT NULL,
        vendor_name VARCHAR(255) NOT NULL,
        status ENUM('active', 'expired') NOT NULL,
        email_sent ENUM('yes', 'no') NOT NULL,
        file_upload VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,

    """
       CREATE TABLE IF NOT EXISTS  expiry_emails(
        id CHAR(36) PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL        
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS password_reset(
        id CHAR(36) PRIMARY KEY,
        reset_token VARCHAR(255) NOT NULL,
        reset_token_expiry  TIMESTAMP NOT NULL,
        used_reset_token ENUM('yes', 'no') NOT NULL,
        user_id CHAR(36) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """
]

async def create_tables():
    with closing(pymysql.connect(**DB_CONFIG)) as connection:
            with closing(connection.cursor()) as cursor:
                for query in queries:
                   cursor.execute(query)
                connection.commit()