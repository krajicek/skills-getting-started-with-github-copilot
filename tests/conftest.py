import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Arrange: Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities(client):
    """Arrange: Reset activities to known state before each test"""
    # Reset the in-memory database to initial state
    from src import app as app_module
    app_module.activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        }
    }
    return app_module.activities
