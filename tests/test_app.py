"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities(self, client):
        """Test that we can retrieve all activities"""
        # Arrange
        # (No setup needed - activities are pre-populated in the app)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Verify structure of an activity
        first_activity = list(activities.values())[0]
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""

    def test_signup_valid_activity(self, client):
        """Test signing up for a valid activity"""
        # Arrange
        email = "student@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_invalid_activity(self, client):
        """Test signing up for a non-existent activity"""
        # Arrange
        email = "student@mergington.edu"
        invalid_activity = "Nonexistent Club"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_student(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        # Arrange
        email = "duplicate@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()

    def test_signup_participant_added_to_list(self, client):
        """Test that a signed-up participant appears in the activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Programming Class"
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity]["participants"])
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        updated_activities = client.get("/activities").json()
        
        # Assert
        assert response.status_code == 200
        assert len(updated_activities[activity]["participants"]) == initial_count + 1
        assert email in updated_activities[activity]["participants"]


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_valid_participant(self, client):
        """Test unregistering a participant from an activity"""
        # Arrange
        email = "removetest@mergington.edu"
        activity = "Gym Class"
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        updated_activities = client.get("/activities").json()
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email not in updated_activities[activity]["participants"]

    def test_unregister_invalid_activity(self, client):
        """Test unregistering from a non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        invalid_activity = "Nonexistent Club"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404

    def test_unregister_non_registered_student(self, client):
        """Test unregistering a student who is not registered"""
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()


class TestRootEndpoint:
    """Tests for the / endpoint"""

    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        # Arrange
        # (No setup needed - root endpoint is pre-configured)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"
