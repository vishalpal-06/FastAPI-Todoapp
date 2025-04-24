from sqlalchemy.orm import Session
from database import sessionlocal
from models import Users

def truncate_table(new_user):
    db: Session = sessionlocal()
    try:
        # db.execute("DELETE FROM todos")  # Replace 'users' with your table name
        db.add(new_user)
        db.commit()
    finally:
        db.close()


new_user = Users(
    email="test@example.com",
    username="testuser",
    first_name="John",
    last_name="Doe",
    hashed_password="pass",  # Store securely
    is_active=True,
    role="admin"
)
truncate_table(new_user)
