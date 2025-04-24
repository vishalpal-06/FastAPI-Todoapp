from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABSE_URL = 'sqlite:///./todosapp.db'

engine = create_engine(SQLALCHEMY_DATABSE_URL, connect_args={'check_same_thread':False})

sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

