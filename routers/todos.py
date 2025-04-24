from fastapi import APIRouter, Depends, HTTPException, Path, status
from utils.database import sessionlocal
from typing import Annotated
from sqlalchemy.orm import Session
from utils.models import Todos
from schema.tables_schema import TodoCreateRequest, TodoUpdateRequest
from .auth import get_current_user


router = APIRouter(
    prefix='/todos',
    tags=['Todos']
)


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# Get all record from database
@router.get("/all/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()




# Get record by id from database
@router.get("/{title}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency,title: str):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.title == title).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='this id is not exist in database')



#
@router.post("/todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoCreateRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = Todos(**todo_request.dict(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()



#
@router.put("/{todo_id}", status_code=status.HTTP_201_CREATED)
async def update_todo(user: user_dependency, db:db_dependency, 
                      todo_request: TodoUpdateRequest,
                      todo_id: int = Path(gt=0) 
                      ):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    print(todo_request)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Id not found in database")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.status = todo_request.status

    db.add(todo_model)
    db.commit()




@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Id not found in database")
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
    db.commit()





