from typing import Annotated, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Path
from ..database import SessionLocal
from ..models import Todos
from .auth import get_current_user

router = APIRouter(
    tags=['todos']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=30)
    description: str = Field(max_length=100)
    priority: int = Field(ge=1, le=5)
    complete: bool
        

@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(401, 'authentication failed')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(401, 'authentication failed')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail='todo not found')    
    return todo_model


@router.post('/todo', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if not user:
        raise HTTPException(401, 'authentication failed')
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()


@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(401, 'authentication failed')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.id == user.get('id')).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail='todo not found')

    todo_model.title = todo_request.title if todo_request.title is not None else todo_model.title
    todo_model.description = todo_request.description if todo_request.description is not None else todo_model.description
    todo_model.priority = todo_request.priority if todo_request.priority is not None else todo_model.priority
    todo_model.complete = todo_request.complete if todo_request.complete is not None else todo_model.complete
    
    db.add(todo_model)
    db.commit()
    

@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(401, 'authentication failed')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail='todo not found')

    db.delete(todo_model)
    db.commit()