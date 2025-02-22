from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import StaticPool
from database import Base
from main import app
from routers.todos import get_db, get_current_user
from fastapi.testclient import TestClient
from main import app
from models import Users, Todos
from routers.auth import bcrypt_context
import pytest

SQLALCHEMY_DATABSE_URL = 'sqlite:///./testdb.db'

engine = create_engine(SQLALCHEMY_DATABSE_URL, connect_args={'check_same_thread':False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return { 
        "id":1,
        "username": "vishal", 
        "email": "vishalpal@gmail.com", 
        "first_name": "vishal kumar", 
        "last_name": "pal", 
        "password": "vishal@06", 
        "role": "admin" }

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


client = TestClient(app)




@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()





@pytest.fixture
def test_user():
    user = Users(
        username="vishalpal-06",
        email="vishalpal@email.com",
        first_name="Vishal",
        last_name="Pal",
        hashed_password=bcrypt_context.hash("testpassword"),
        role="admin",
        phone_number="(111)-111-1111"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()