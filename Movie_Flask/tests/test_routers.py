import pytest
import pathlib, sys 
import mongomock
from app import get_mongo_db

sys.path.append(str(pathlib.Path(__file__).parent.parent))
from models import User

def test_register_user(client, monkeypatch):
    test_user_data = {
        "first_name":"Demouser",
        "last_name": "3",
        "email": "demouser3@gmail.com",
        "login_id": "demouser3",
        "password": "demouser@3",
        "confirm_password": "demouser@3",
        "contact_number": 9876543210,
        "security_question": "What is your father's name",
        "security_answer": "Robert"
    }
    response = client.post('/api/v1.0/moviebooking/register', json=test_user_data)
    assert response.status_code == 201
    assert b"User registered successfully" in response.data
    users_collection = get_mongo_db().users
    users_collection.delete_one({'email': test_user_data['email']})

def test_register_user_when_email_already_present(client):
    test_user_data = {
        "first_name":"Demouser",
        "last_name": "3",
        "email": "demouser2@gmail.com",
        "login_id": "demouser2",
        "password": "demouser@2",
        "confirm_password": "demouser@2",
        "contact_number": 9876543210,
        "security_question": "What is your father's name",
        "security_answer": "Robert"
    }
    response = client.post('/api/v1.0/moviebooking/register', json=test_user_data)
    assert response.status_code == 409
    assert b"Email already registered" in response.data

def test_register_user_when_loginid_already_present(client):
    test_user_data = {
        "first_name":"Demouser",
        "last_name": "3",
        "email": "demouser1@gmail.com",
        "login_id": "demouser2",
        "password": "demouser@2",
        "confirm_password": "demouser@2",
        "contact_number": 9876543210,
        "security_question": "What is your father's name",
        "security_answer": "Robert"
    }
    response = client.post('/api/v1.0/moviebooking/register', json=test_user_data)
    assert response.status_code == 409
    assert b"Login ID already taken" in response.data

def test_register_user_with_invalid_request_body(client):
    test_user_data = {
        "first_name":"Demouser",
        "email": "demouser1@gmail.com",
        "login_id": "demouser2",
        "password": "demouser@2",
        "confirm_password": "demouser@2",
        "contact_number": 9876543210,
        "security_question": "What is your father's name",
        "security_answer": "Robert"
    }
    response = client.post('/api/v1.0/moviebooking/register', json=test_user_data)
    assert response.status_code == 400

def test_register_user_with_password_mismatch(client):
    test_user_data = {
        "first_name":"Demouser",
        "last_name": "3",
        "email": "demouser1@gmail.com",
        "login_id": "demouser2",
        "password": "demouser@2",
        "confirm_password": "demouser@21",
        "contact_number": 9876543210,
        "security_question": "What is your father's name",
        "security_answer": "Robert"
    }
    response = client.post('/api/v1.0/moviebooking/register', json=test_user_data)
    assert response.status_code == 400

def test_login(client):
    test_user_data = {
    "login_id": "demouser2",
    "password": "demouser@2"
    }
    response = client.post('/api/v1.0/moviebooking/login', json=test_user_data)
    assert response.status_code == 200

def test_login_invalid_credentials(client):
    test_user_data = {
    "login_id": "demouser2",
    "password": "demouser@21"
    }
    response = client.post('/api/v1.0/moviebooking/login', json=test_user_data)
    assert response.status_code == 401

def test_forgot_password(client):
    test_user_data = {
    "email":"demouser2@gmail.com"
    }
    response = client.post('/api/v1.0/moviebooking/forgot', json=test_user_data)
    assert response.status_code == 200

def test_reset_password(client):
    test_user_data= {
    "email": "demouser2@gmail.com",
    "security_answer": "Robbert",
    "password": "demouser@2",
    "confirm_password": "demouser@2"
    }
    response = client.post('/api/v1.0/moviebooking/resetpassword', json=test_user_data)
    assert response.status_code == 200

def test_get_all_movies(client):
    response = client.get('/api/v1.0/moviebooking/all')
    assert response.status_code == 200

def test_search_movie(client):
    response = client.get('/api/v1.0/moviebooking/movies/search/opp')
    assert response.status_code == 200

def test_book_tickets(client):
    test_user_data = {
    "email": "demouser2@gmail.com",
    "theatre_name": "PVR",
    "num_tickets": 1
    }
    response = client.post('/api/v1.0/moviebooking/oppenHeimer/add', json = test_user_data)
    assert response.status_code == 200

def test_get_booked_tickets(client):
    response = client.get('/api/v1.0/moviebooking/bookedtickets/demouser2@gmail.com')
    assert response.status_code == 200

