from .utils import *
from ..routers.users import get_current_user, get_db
from fastapi import status
from ..main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_current_user(test_user):
    response = client.get('/users/current-user')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'johndoe'
    assert response.json()['first_name'] == 'John'
    assert response.json()['last_name'] == 'Doe'
    assert response.json()['role'] == 'admin'
    assert response.json()['is_active'] == True


