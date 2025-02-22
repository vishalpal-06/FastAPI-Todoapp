from fastapi import APIRouter, Depends, HTTPException, Path, status
from database import sessionlocal
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from schema.tables_schema import TodoRequest
from .auth import get_current_user
from models import Users


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