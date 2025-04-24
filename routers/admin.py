from fastapi import APIRouter, Depends, HTTPException, Path, status, Body
from utils.database import sessionlocal
from typing import Annotated,Optional,Literal
from pydantic import BaseModel, EmailStr, Field, constr
from sqlalchemy.orm import Session
from utils.models import Todos
from schema.tables_schema import CreateUserRequest
from .auth import get_current_user
from utils.models import Users
from passlib.hash import bcrypt

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



@router.get("/all_todos", status_code=status.HTTP_200_OK)
def read_all_todos(user:user_dependency, db:db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could Not Validate User As Admin.")
    return db.query(Todos).all()



@router.get("/read_all_users/", status_code=status.HTTP_200_OK)
async def read_all_users(user:user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could Not Validate User As Admin.")
    return db.query(Users).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could Not Validate User As Admin.")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo Id not found in database")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()



@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could Not Validate User As Admin.")
    todo_model = db.query(Users).filter(Users.id == user_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="User Id not found in database")
    db.query(Users).filter(Users.id == user_id).delete()
    db.query(Todos).filter(Todos.owner_id == user_id).delete()
    db.commit()


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None


@router.put("/user/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(
    user: user_dependency,
    db: db_dependency,
    user_id: int = Path(gt=0),
    user_update: UpdateUserRequest = Body(...)
):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could Not Validate User As Admin.")
    
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User Id not found in database")
    
    # Update only provided fields
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_model, key, value)
    
    db.add(user_model)
    db.commit()
    db.refresh(user_model)




@router.post("/user", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: user_dependency,
    db: db_dependency,
    new_user: CreateUserRequest = Body(...)
):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only admins can create users."
        )

    # Check if email or username already exists
    existing_user = db.query(Users).filter(
        (Users.email == new_user.email) | (Users.username == new_user.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already exists."
        )

    # Create new user
    user_model = Users(
        email=new_user.email,
        username=new_user.username,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        role=new_user.role,
        hashed_password=bcrypt.hash(new_user.password)
    )

    db.add(user_model)
    db.commit()
    db.refresh(user_model)
