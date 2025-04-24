from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime
from datetime import datetime, timedelta
import enum

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    role = Column(String)

class Priority(enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"

class Status(enum.Enum):
    Pending = "Pending"
    Completed = "Completed"


def get_ist_time():
    utc_time = datetime.utcnow()
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time

class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Enum(Priority), default=Priority.Low)
    status = Column(Enum(Status), default=Status.Completed)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=get_ist_time)
    updated_at = Column(DateTime, default=get_ist_time, onupdate=get_ist_time)
