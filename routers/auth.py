from fastapi import APIRouter, Depends, HTTPException, Path, status, Body, UploadFile, File
from schema.tables_schema import CreateUserRequest
from utils.models import Users
from passlib.context import CryptContext
from utils.database import sessionlocal
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from pydantic import BaseModel, EmailStr, Field
from azure.storage.blob import BlobServiceClient
from fastapi.responses import StreamingResponse
from io import BytesIO
import yaml

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
    userdata: dict




def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()




def authenticate_user(username: str, password: str, db):
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
        user_firstname: str = payload.get('firstname')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Cloud Not Validate User.')
        return {'username': username, 'id':user_id, 'user_role':user_role }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Cloud Not Validate User.')

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could Not Validate User.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=60))
    # Include user role in the response
    return {
        'access_token': token,
        'token_type': 'bearer',
        'userdata': {
            'username': user.username,
            'role': user.role
        }
    }





class UserDetailsResponse(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: bool

    class Config:
        orm_mode = True

@router.get("/user_details/", status_code=status.HTTP_200_OK)
async def get_user_details(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserDetailsResponse(
        id=user_model.id,
        username=user_model.username,
        first_name=user_model.first_name,
        last_name=user_model.last_name,
        email=user_model.email,
        role=user_model.role,
        is_active=user_model.is_active
    )





class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@router.put("/user/updateprofile", status_code=status.HTTP_200_OK)
async def update_user(
    user: user_dependency,
    db: db_dependency,
    user_update: UpdateUserRequest = Body(...)
):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User Id not found in database")
    
    # Update only provided fields
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_model, key, value)
    
    db.add(user_model)
    db.commit()
    db.refresh(user_model)





def upload_blob(connection_string, container_name, file_data, blob_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        blob_client.upload_blob(file_data, overwrite=True)

        print(f"File uploaded to blob '{blob_name}' successfully.")
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise



@router.post("/createprofilepic/", status_code=status.HTTP_201_CREATED)
async def upload_profile_pic(user: user_dependency, db: db_dependency, image: UploadFile = File(...)):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User Id not found in database")

    blob_name = user_model.username + ".jpg"

    with open('Config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    connection_string = config['blob']['Connection_string']
    container_name = "profilepics"

    file_data = await image.read()  # Read file content from UploadFile
    upload_blob(connection_string, container_name, file_data, blob_name)

    return {"filename": image.filename, "message": "Upload successful"}


@router.get("/getprofilepic/", status_code=status.HTTP_200_OK)
async def get_profile_picture(user: user_dependency):
    try:
        with open('Config.yaml', 'r') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        connection_string = config['blob']['Connection_string']
        container_name = "profilepics"
        blob_name = user.get('username') + ".jpg"

        blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        stream = blob_client.download_blob()
        file_bytes = stream.readall()

        return StreamingResponse(BytesIO(file_bytes), media_type="image/jpeg")

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Image not found or error retrieving it: {str(e)}")
