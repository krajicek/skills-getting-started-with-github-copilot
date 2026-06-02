"""
Test suite for Mergington High School API endpoints.
Uses AAA (Arrange-Act-Assert) pattern for test structure.
"""


class TestRootEndpoint:
    def test_root_redirect(self, client):
        """
        Arrange: Already have test client
        Act: Make GET request to root endpoint
        Assert: Verify redirect to static/index.html
        """
        # Arrange: test client is provided by fixture

        # Act: Make request
        response = client.get("/", follow_redirects=False)

        # Assert: Check redirect status and location
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestActivitiesEndpoint:
    def test_get_activities_returns_all(self, client, reset_activities):
        """
        Arrange: Reset activities to known state
        Act: Fetch all activities
        Assert: Verify response contains all activities
        """
        # Arrange: Activities reset by fixture
        expected_count = len(reset_activities)

        # Act: Make GET request
        response = client.get("/activities")

        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_count
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["max_participants"] == 12

    def test_get_activities_structure(self, client, reset_activities):
        """
        Arrange: Reset activities
        Act: Fetch activities
        Assert: Verify each activity has required fields
        """
        # Arrange: Activities reset by fixture

        # Act: Make request
        response = client.get("/activities")
        data = response.json()

        # Assert: Check structure of each activity
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_participants_list(self, client, reset_activities):
        """
        Arrange: Activities with known participants
        Act: Fetch activities
        Assert: Verify participants data matches
        """
        # Arrange: Activities with known state
        assert "michael@mergington.edu" in reset_activities["Chess Club"]["participants"]
        assert len(reset_activities["Programming Class"]["participants"]) == 0

        # Act: Fetch activities
        response = client.get("/activities")
        data = response.json()

        # Assert: Verify participants data
        assert data["Chess Club"]["participants"] == ["michael@mergington.edu"]
        assert data["Programming Class"]["participants"] == []


class TestSignupEndpoint:
    def test_signup_new_participant_success(self, client, reset_activities):
        """
        Arrange: Verify participant not already signed up
        Act: Sign up new participant
        Assert: Verify participant added to activity
        """
        # Arrange: Fresh state from fixture
        activity = "Programming Class"
        email = "newstudent@mergington.edu"
        initial_count = len(reset_activities[activity]["participants"])

        # Act: Sign up participant
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert: Verify success
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in reset_activities[activity]["participants"]
        assert len(reset_activities[activity]["participants"]) == initial_count + 1

    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """
        Arrange: Use participant already in activity
        Act: Attempt to sign up same participant again
        Assert: Verify 400 error returned
        """
        # Arrange: Get existing participant
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act: Attempt duplicate signup
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert: Verify error
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """
        Arrange: Use activity name that doesn't exist
        Act: Attempt to sign up for nonexistent activity
        Assert: Verify 404 error returned
        """
        # Arrange: Setup with nonexistent activity name
        activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act: Attempt signup
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert: Verify 404
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_multiple_participants_different_activities(self, client, reset_activities):
        """
        Arrange: Multiple activities in system
        Act: Sign up same participant to different activities
        Assert: Verify participant appears in both
        """
        # Arrange: Setup
        email = "versatile@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Act: Sign up for both activities
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )

        # Assert: Verify success and presence in both
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in reset_activities[activity1]["participants"]
        assert email in reset_activities[activity2]["participants"]


class TestUnregisterEndpoint:
    def test_unregister_participant_success(self, client, reset_activities):
        """
        Arrange: Verify participant is in activity
        Act: Delete participant from activity
        Assert: Verify participant removed
        """
        # Arrange: Get existing participant
        activity = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(reset_activities[activity]["participants"])
        assert email in reset_activities[activity]["participants"]

        # Act: Unregister participant
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )

        # Assert: Verify removed
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email not in reset_activities[activity]["participants"]
        assert len(reset_activities[activity]["participants"]) == initial_count - 1

    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """
        Arrange: Use activity that doesn't exist
        Act: Attempt to unregister from nonexistent activity
        Assert: Verify 404 error returned
        """
        # Arrange: Nonexistent activity
        activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act: Attempt unregister
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )

        # Assert: Verify 404
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """
        Arrange: Use participant not in activity
        Act: Attempt to unregister participant not signed up
        Assert: Verify 404 error returned
        """
        # Arrange: Participant not in activity
        activity = "Programming Class"
        email = "notinactivity@mergington.edu"

        # Act: Attempt unregister
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )

        # Assert: Verify 404
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_then_signup_again(self, client, reset_activities):
        """
        Arrange: Have participant in activity
        Act: Unregister then sign up again
        Assert: Verify participant can re-register
        """
        # Arrange: Setup
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act: Unregister
        response1 = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        assert email not in reset_activities[activity]["participants"]

        # Act: Sign up again
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert: Verify success
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in reset_activities[activity]["participants"]

    def test_unregister_from_empty_activity(self, client, reset_activities):
        """
        Arrange: Activity with no participants
        Act: Attempt to unregister from empty activity
        Assert: Verify 404 error for missing participant
        """
        # Arrange: Programming Class has no participants
        activity = "Programming Class"
        email = "someone@mergington.edu"
        assert len(reset_activities[activity]["participants"]) == 0

        # Act: Attempt unregister
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )

        # Assert: Verify 404
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestIntegrationScenarios:
    def test_signup_unregister_signup_flow(self, client, reset_activities):
        """
        Arrange: Empty activity
        Act: Sign up, unregister, sign up, verify state
        Assert: Final state matches expectations
        """
        # Arrange: Setup
        activity = "Programming Class"
        email = "user@mergington.edu"

        # Act: Initial signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert: First signup succeeds
        assert response1.status_code == 200
        assert email in reset_activities[activity]["participants"]

        # Act: Unregister
        response2 = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )

        # Assert: Unregister succeeds
        assert response2.status_code == 200
        assert email not in reset_activities[activity]["participants"]

        # Act: Sign up again
        response3 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert: Second signup succeeds
        assert response3.status_code == 200
        assert email in reset_activities[activity]["participants"]

    def test_multiple_participants_single_activity(self, client, reset_activities):
        """
        Arrange: Activity with one participant
        Act: Add multiple new participants
        Assert: All participants present in activity
        """
        # Arrange: Chess Club has michael@mergington.edu
        activity = "Chess Club"
        participants = [
            "alice@mergington.edu",
            "bob@mergington.edu",
            "carol@mergington.edu"
        ]

        # Act: Add new participants
        for email in participants:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert: All participants present
        for email in participants:
            assert email in reset_activities[activity]["participants"]
        assert len(reset_activities[activity]["participants"]) == 4  # 1 original + 3 new

    def test_response_messages_format(self, client, reset_activities):
        """
        Arrange: Prepare activity and participant data
        Act: Perform signup and unregister operations
        Assert: Verify response messages contain relevant data
        """
        # Arrange: Setup
        activity = "Programming Class"
        email = "user@mergington.edu"

        # Act: Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert: Check signup message format
        signup_msg = signup_response.json()["message"]
        assert email in signup_msg
        assert activity in signup_msg

        # Act: Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )

        # Assert: Check unregister message format
        unregister_msg = unregister_response.json()["message"]
        assert email in unregister_msg
        assert activity in unregister_msg
