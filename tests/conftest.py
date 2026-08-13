"""Pytest configuration and fixtures for API tests."""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for making requests to the app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset the global activities dictionary to its initial state before each test.
    This fixture runs automatically to ensure test isolation.
    """
    # Store the original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for interscholastic play",
            "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn and practice tennis skills on the court",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu", "emily@mergington.edu"]
        },
        "Art Studio": {
            "description": "Create paintings, drawings, and sculptures",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Theater Club": {
            "description": "Perform in theatrical productions and musicals",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["sophia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills through competitive debate",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": ["christopher@mergington.edu", "madison@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific experiments and conduct research projects",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["benjamin@mergington.edu"]
        }
    }

    # Clear the current activities and reset with a deep copy of original
    activities.clear()
    activities.update(copy.deepcopy(original_activities))

    yield

    # Cleanup after test
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


@pytest.fixture(autouse=True)
def _reset_activities_autouse(reset_activities):
    """Auto-use fixture to reset activities before each test."""
    pass


@pytest.fixture
def test_data():
    """Provide common test data for tests to use."""
    return {
        "new_student_email": "newstudent@mergington.edu",
        "existing_student_email": "michael@mergington.edu",
        "activity_with_participants": "Chess Club",
        "activity_full": "Basketball Team",  # Only has 1/15 spots, use another if needed
        "nonexistent_activity": "Underwater Basket Weaving",
    }
