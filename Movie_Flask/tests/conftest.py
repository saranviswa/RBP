import pytest
import mongomock
import json
import pathlib, sys 
import os 
from unittest.mock import patch
sys.path.append(str(pathlib.Path(__file__).parent.parent))
from app import app

@pytest.fixture(scope='session')
def client():
    with app.test_client() as client:
        yield client


