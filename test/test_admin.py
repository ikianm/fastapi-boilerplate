from .utils import *
from ..routers.admin import get_db, get_current_user
from ..main import app
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_authenticated(test_todo):
    response = client.get('/admin/todo')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'complete': False,
        'title': 'learn to code',
        'description': 'need to learn everyday',
        'priority': 5,
        'owner_id': 1,
        'id': 1
    }]
    

def test_admin_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None
    

def test_admin_delete_todo_not_found(test_todo):
    response = client.delete('/todo/2')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    