from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import Field, BaseModel
from passlib.context import CryptContext
from ..database import SessionLocal
from ..models import Users
from .auth import get_current_user


router = APIRouter(
    prefix='/users',
    tags=['users']
)


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class ChangePasswordRequest(BaseModel):
    new_password: str = Field(min_length=4)


@router.get('/current-user')
async def current_user(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(401, 'authentication failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if not user_model:
        raise HTTPException(404, 'no user found')
    
    return user_model


@router.patch('/change-password')
async def change_password(user: user_dependency, db: db_dependency, change_password_request: ChangePasswordRequest):
    if not user:
        raise HTTPException(401, 'authentication failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if not user_model:
        raise HTTPException(404, 'no user found')
    
    if bcrypt_context.verify(change_password_request.new_password, user_model.hashed_password):
        raise HTTPException(400, 'password is same as the old one')
    
    user_model.hashed_password = bcrypt_context.hash(change_password_request.new_password)
    db.add(user_model)
    db.commit()
    
    