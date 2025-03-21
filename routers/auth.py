from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, status, Depends, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from ..database import SessionLocal
from ..models import Users

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY='d83865e697d62ee1bd9bb0df2d4ff2f1ae2d88963c2a24a1c88ce4bebc6858f0'
ALGORITHM='HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    payload = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    payload.update({'exp': expires})
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if not username or not user_id or not user_role:
            raise HTTPException(401, 'Could not validate user')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(401, 'Could not validate user')


class Token(BaseModel):
    access_token: str
    token_type: str
    
class CreateUserRequest(BaseModel): 
    username: str
    email: str 
    first_name: str
    last_name: str
    password: str
    role: str



@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )
    
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    
    return create_user_model


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
    ):
    
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(401, 'Invalid username or password')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {
        "access_token": token,
        "token_type": "bearer"
    }
    