import copy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
initial_activities = copy.deepcopy(activities)


def pytest_configure(config):
    # Ensure pytest imports the app package correctly when running from repo root
    return


def reset_activities_state():
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))


def setup_function(function):
    reset_activities_state()


def teardown_function(function):
    reset_activities_state()


def test_get_activities_returns_activity_list():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_new_participant_adds_participant():
    activity_name = "Chess Club"
    new_email = "teststudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup?email={new_email}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup?email={existing_email}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_unsubscribes_participant():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants?email={email}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_400():
    activity_name = "Chess Club"
    missing_email = "missing@student.com"

    response = client.delete(
        f"/activities/{activity_name}/participants?email={missing_email}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Participant not found for this activity"
