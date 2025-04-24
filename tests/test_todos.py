import pytest
from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import func
from tests.utils import client,TestingSessionLocal,test_todo
from utils.models import Todos


def test_create_todo(test_todo):
    request_data={
        'title': 'Test Todo!',
        'description':'Test todo description',
        'priority': 5,
        'complete': False,
    }

    response = client.post('/todos/todo/', json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_get_all_todos():
    response = client.get('/todos/all/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]['id'] == 1
    assert data[0]['title'] == 'Test Todo!'
    assert data[0]['priority'] == 5
    assert data[0]['description'] == 'Test todo description'
    assert data[0]['complete'] == False
    assert data[0]['owner_id'] == 1


def test_get_todo_by_id():
    response = client.get('/todos/1')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == 1
    assert data['title'] == 'Test Todo!'
    assert data['priority'] == 5
    assert data['description'] == 'Test todo description'
    assert data['complete'] == False
    assert data['owner_id'] == 1


def test_update_todo():
    update_request = {
        'title': 'Updated Test Todo!',
        'description':'Updated Test todo description',
        'priority': 2,
        'complete': True,
    }
    db = TestingSessionLocal()

    todo_model = db.query(Todos).filter(Todos.id == 1).filter(Todos.owner_id == 1).first()

    response = client.put('/todos/1',json=update_request)

    todo_model = db.query(Todos).filter(Todos.id == 1).filter(Todos.owner_id == 1).first()
    db.commit()

    assert todo_model.title == update_request['title']
    assert todo_model.description == update_request['description']
    assert todo_model.priority == update_request['priority']
    assert todo_model.complete == update_request['complete']


def test_delete_todo():
    db = TestingSessionLocal()
    response = client.delete('/todos/1')
    assert response.status_code == 204
    









