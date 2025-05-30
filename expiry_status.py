import pymysql
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os

#
current_directory = Path(__file__).resolve().parent if '__file__' in locals() else Path.cwd()
env_file = current_directory / '.env'
print(f"expiry status: {env_file}")
load_dotenv(env_file)
# load_dotenv("/backend-kl/.env")

user = os.getenv('DB_USER_LOCAL')
localhost = os.getenv('DB_HOST')
password= os.getenv('DB_PASSWORD')
database= os.getenv('DB_DATABASE')
print(f'user: {user}, localhost: {localhost}, password: {password}, database: {database}')



def change_status():
    db = pymysql.connect(
        host=localhost,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )


    today = datetime.now()
    with db.cursor() as cursor:
        try:
            query = """
            SELECT * FROM KlContract.contracts WHERE status = 'active'
            """
            cursor.execute(query)
            contracts = cursor.fetchall()
            for contract in contracts:
                end_date = contract['end_date']
                if end_date <= today.date():
                    try:
                        query = """
                        UPDATE KlContract.contracts SET status = 'expired' WHERE id = %s
                        """
                        cursor.execute(query, contract['id'])
                        print(f'Contract expired: {contract["contract_name"]}, time: {datetime.now()}')
                        db.commit()

                    except Exception as e:
                        print(f'Error updating contract expired: {e} time: {datetime.now()}')
        except Exception as e:
            print(f'Error fetching contracts: {e}, time: {datetime.now()}')
        finally:
            db.close()


# cron job running daily
if __name__ == '__main__':
    change_status()

