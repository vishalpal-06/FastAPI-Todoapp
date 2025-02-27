from fastapi import APIRouter, Depends, HTTPException, Path, status
from schema.tables_schema import CreateUserRequest
from models import Users
from passlib.context import CryptContext
from database import sessionlocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from pydantic import BaseModel


router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)

SECRET_KEY = 'd2e2b8fe4827c93ad7ac831a45b2f28c6f33e04f975c0b4b2b1b8d8b38d694a4'
ALGORITHUM = 'HS256'
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class Token(BaseModel):
    access_token: str
    token_type: str




def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]




def authenticate_user(username: str, password: str, db):
    print("function triggers")
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if bcrypt_context.verify(password, user.hashed_password):
        return user
    return False




def create_access_token(username:str, user_id: int, role:str, expries_delta: timedelta):
    encode = {
        'sub': username, 
        'id': user_id,
        'role': role
    }
    expires = datetime.now(timezone.utc) + expries_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHUM)




async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHUM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, details='Cloud Not Validate User.')
        return {'username': username, 'id':user_id, 'user_role':user_role }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, details='Cloud Not Validate User.')




@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_requiest: CreateUserRequest):
    create_user_model = Users(
        email=create_user_requiest.email,
        username=create_user_requiest.username,
        first_name=create_user_requiest.first_name,
        last_name=create_user_requiest.last_name,
        hashed_password=bcrypt_context.hash(create_user_requiest.password),
        is_active=True,
        role=create_user_requiest.role
    )
    db.add(create_user_model)
    db.commit()




@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, details='Cloud Not Validate User.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type':'bearer'}













