from sqlalchemy.orm import Session
from tests.utils import TestingSessionLocal

def truncate_table():
    db: Session = TestingSessionLocal()
    try:
        db.execute("DELETE FROM todos")  # Replace 'users' with your table name
        db.commit()
    finally:
        db.close()


truncate_table()
