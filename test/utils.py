import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..models import Todos, Users
from ..main import app
from ..routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def override_get_current_user():
    return {'username': 'johndoe', 'id': 1, 'user_role': 'admin'} 

client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title="learn to code",
        description="need to learn everyday",
        priority=5,
        complete=False,
        owner_id=1 # same id as user dependency
    )
    
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM todos;'))
        connection.commit()
    
    
@pytest.fixture
def test_user():
    user = Users(
        email='john@gmail.com',
        username='johndoe',
        first_name='John',
        last_name='Doe',
        hashed_password=bcrypt_context.hash('1234'),
        is_active=True,
        role='admin'
    )
    
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users;'))
        connection.commit()