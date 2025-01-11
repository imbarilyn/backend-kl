from sql_app import models
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from contextlib import contextmanager
from sql_app.database import SessionLocal
import sys
import os

# Add the parent directory of sql_app to the Python path

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append()

@contextmanager
def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.close()


def change_status(db: Session):
    today = datetime.now()
    expired_contracts = db.query(models.Contract).filter(
       models.Contract.end_date <= today.strftime('%Y-%m-%d')).all()
    if expired_contracts:
        for contract in expired_contracts:
            contract.status = 0
            db.commit()


with get_db() as database_session:
    change_status(database_session)
    print(f"Status changed successfully {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Completely out of the context manager code block")
