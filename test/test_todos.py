from fastapi import status
from ..main import app
from ..routers.todos import get_db, get_current_user
from ..models import Todos
from .utils import *
        
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_read_all_authenticated(test_todo):
    response = client.get('/')
    assert response.status_code ==  status.HTTP_200_OK
    assert response.json() == [
            {
                "id": 1,
                "title": "learn to code", 
                "description": "need to learn everyday", 
                "priority": 5,
                "complete": False,
                "owner_id": 1
            }
        ]
    
    
def test_read_one_authenticated(test_todo):
    response = client.get('/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
                "id": 1,
                "title": "learn to code", 
                "description": "need to learn everyday", 
                "priority": 5,
                "complete": False,
                "owner_id": 1
            }
        

def test_read_one_authenticated_not_found(test_todo):
    response = client.get('/todo/2')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "todo not found"}
    
    
def test_create_todo(test_todo):
    request_body = {
        'title': 'new todo',
        'description': 'some description',
        'priority': 4,
        'complete': False
    }
    response = client.post('/todo', json=request_body)
    assert response.status_code == status.HTTP_201_CREATED
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first() # fixture already created a todo with id 1
    assert model.title == request_body.get('title')
    assert model.description == request_body.get('description')
    assert model.priority == request_body.get('priority')
    assert model.complete == request_body.get('complete')
    

def test_update_todo(test_todo):
    request_body = {
        "title": "updated title",
        "description": "updated description",
        "priority": 1,
        "complete": True
    }
    response = client.put('/todo/1', json=request_body)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_body.get('title')
    assert model.description == request_body.get('description')
    assert model.priority == request_body.get('priority')
    assert model.complete == request_body.get('complete')
        

def test_update_todo_not_found(test_todo):
    request_body = {
        "title": "updated title",
        "description": "updated description",
        "priority": 1,
        "complete": True
    }
    response = client.put('/todo/2', json=request_body)
    assert response.status_code == status.HTTP_404_NOT_FOUND  
    

def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model == None
    
    

def test_delete_todo_not_found(test_todo):
    response = client.delete('/todo/2')
    assert response.status_code == status.HTTP_404_NOT_FOUND