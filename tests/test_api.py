"""FastAPI endpoint tests using AAA (Arrange-Act-Assert) pattern."""

import pytest
from src.app import activities


class TestRoot:
    """Tests for GET / (root) endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        ARRANGE: Prepare the test client
        ACT: Make a GET request to /
        ASSERT: Verify redirect to /static/index.html
        """
        # Arrange & Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        ARRANGE: Prepare the test client
        ACT: Make a GET request to /activities
        ASSERT: Verify all activities are returned
        """
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_includes_all_required_fields(self, client):
        """
        ARRANGE: Prepare the test client
        ACT: Make a GET request to /activities
        ASSERT: Verify each activity has required fields
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_preserves_participant_list(self, client):
        """
        ARRANGE: Prepare the test client with known activity state
        ACT: Make a GET request to /activities
        ASSERT: Verify participant count matches expected
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_student_success(self, client, test_data):
        """
        ARRANGE: Prepare a new student email and activity name
        ACT: POST to signup endpoint
        ASSERT: Verify success response and participant added
        """
        # Arrange
        email = test_data["new_student_email"]
        activity = test_data["activity_with_participants"]

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        assert email in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == 3

    def test_signup_duplicate_student_fails(self, client, test_data):
        """
        ARRANGE: Use an already-registered student
        ACT: POST to signup endpoint with duplicate email
        ASSERT: Verify 400 error and duplicate rejection message
        """
        # Arrange
        email = test_data["existing_student_email"]
        activity = test_data["activity_with_participants"]

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client, test_data):
        """
        ARRANGE: Use a nonexistent activity name
        ACT: POST to signup endpoint with invalid activity
        ASSERT: Verify 404 error
        """
        # Arrange
        email = test_data["new_student_email"]
        activity = test_data["nonexistent_activity"]

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_multiple_students_accumulate(self, client):
        """
        ARRANGE: Register multiple students sequentially
        ACT: POST multiple signup requests
        ASSERT: Verify all students are added to participants
        """
        # Arrange
        activity = "Programming Class"
        student1 = "alice@mergington.edu"
        student2 = "bob@mergington.edu"
        initial_count = len(activities[activity]["participants"])

        # Act
        response1 = client.post(
            f"/activities/{activity}/signup?email={student1}",
            params={"email": student1}
        )
        response2 = client.post(
            f"/activities/{activity}/signup?email={student2}",
            params={"email": student2}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(activities[activity]["participants"]) == initial_count + 2
        assert student1 in activities[activity]["participants"]
        assert student2 in activities[activity]["participants"]

    def test_signup_returns_success_message(self, client, test_data):
        """
        ARRANGE: Prepare a new student and activity
        ACT: POST to signup endpoint
        ASSERT: Verify response message includes email and activity name
        """
        # Arrange
        email = test_data["new_student_email"]
        activity = test_data["activity_with_participants"]

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert email in data["message"]
        assert activity in data["message"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_registered_student_success(self, client):
        """
        ARRANGE: Use an already-registered student
        ACT: DELETE to unregister endpoint
        ASSERT: Verify success and participant removed
        """
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        initial_count = len(activities[activity]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count - 1

    def test_unregister_unregistered_student_fails(self, client, test_data):
        """
        ARRANGE: Use a student not registered for the activity
        ACT: DELETE to unregister endpoint
        ASSERT: Verify 400 error and not registered message
        """
        # Arrange
        email = test_data["new_student_email"]
        activity = test_data["activity_with_participants"]

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self, client, test_data):
        """
        ARRANGE: Use a nonexistent activity name
        ACT: DELETE to unregister endpoint with invalid activity
        ASSERT: Verify 404 error
        """
        # Arrange
        email = test_data["new_student_email"]
        activity = test_data["nonexistent_activity"]

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_returns_success_message(self, client):
        """
        ARRANGE: Prepare a registered student
        ACT: DELETE to unregister endpoint
        ASSERT: Verify response message includes email and activity
        """
        # Arrange
        email = "daniel@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert email in data["message"]
        assert activity in data["message"]

    def test_unregister_multiple_participants_sequentially(self, client):
        """
        ARRANGE: Prepare an activity with multiple participants
        ACT: DELETE multiple unregister requests
        ASSERT: Verify all participants are removed correctly
        """
        # Arrange
        activity = "Debate Team"
        student1 = "christopher@mergington.edu"
        student2 = "madison@mergington.edu"
        initial_count = len(activities[activity]["participants"])

        # Act
        response1 = client.delete(
            f"/activities/{activity}/unregister?email={student1}",
            params={"email": student1}
        )
        response2 = client.delete(
            f"/activities/{activity}/unregister?email={student2}",
            params={"email": student2}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(activities[activity]["participants"]) == initial_count - 2
        assert student1 not in activities[activity]["participants"]
        assert student2 not in activities[activity]["participants"]


class TestIntegrationSignupUnregister:
    """Integration tests combining signup and unregister flows."""

    def test_signup_then_unregister_flow(self, client, test_data):
        """
        ARRANGE: Prepare a new student and activity
        ACT: Sign up, verify in list, then unregister
        ASSERT: Verify full flow works and student is removed
        """
        # Arrange
        email = test_data["new_student_email"]
        activity = test_data["activity_with_participants"]

        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )

        # Assert - Student added
        assert signup_response.status_code == 200
        assert email in activities[activity]["participants"]

        # Act - Get activities to verify
        get_response = client.get("/activities")
        activities_data = get_response.json()

        # Assert - Verify in list
        assert email in activities_data[activity]["participants"]

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}",
            params={"email": email}
        )

        # Assert - Student removed
        assert unregister_response.status_code == 200
        assert email not in activities[activity]["participants"]

    def test_signup_refresh_shows_participant(self, client):
        """
        ARRANGE: Sign up a new student
        ACT: Fetch activities to see updated list
        ASSERT: Verify new student appears in participant list
        """
        # Arrange
        email = "testuser@mergington.edu"
        activity = "Art Studio"

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}",
            params={"email": email}
        )

        # Act - Fetch activities
        get_response = client.get("/activities")
        data = get_response.json()

        # Assert
        assert signup_response.status_code == 200
        assert email in data[activity]["participants"]
