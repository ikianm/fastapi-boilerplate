from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .auth import get_current_user
from ..models import Todos

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/todo', status_code=status.HTTP_200_OK)
async def reade_all(user: user_dependency, db: db_dependency):
    if not user or user.get('user_role') != 'admin':
        raise HTTPException(401, 'authentication failed')

    return db.query(Todos).all()


@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int):
    if not user or user.get('user.role') != 'admin':
        raise HTTPException(401, 'authentication failed')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo_model:
        raise HTTPException(404, 'todo not found')
    
    db.delete(todo_model)
    db.commit()

