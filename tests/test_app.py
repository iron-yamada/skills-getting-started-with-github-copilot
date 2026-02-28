import copy
import pytest
from fastapi.testclient import TestClient
from src import app as application

client = TestClient(application.app)
# keep a copy of original activities so tests can reset
_initial_activities = copy.deepcopy(application.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # clear and repopulate before each test
    application.activities.clear()
    application.activities.update(copy.deepcopy(_initial_activities))
    yield


def test_root_redirect():
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    assert r.json() == _initial_activities


def test_signup_success():
    email = "new@mergington.edu"
    activity = "Chess Club"
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in application.activities[activity]["participants"]
    assert r.json() == {"message": f"Signed up {email} for {activity}"}


def test_signup_nonexistent():
    r = client.post("/activities/NoSuch/signup", params={"email": "x@x"})
    assert r.status_code == 404


def test_signup_already_registered():
    existing = application.activities["Chess Club"]["participants"][0]
    r = client.post("/activities/Chess Club/signup", params={"email": existing})
    assert r.status_code == 400


def test_unregister_success():
    email = application.activities["Programming Class"]["participants"][0]
    r = client.post(
        "/activities/Programming Class/unregister", params={"email": email}
    )
    assert r.status_code == 200
    assert email not in application.activities["Programming Class"]["participants"]


def test_unregister_nonexistent_activity():
    r = client.post("/activities/NoSuch/unregister", params={"email": "x@x"})
    assert r.status_code == 404


def test_unregister_not_registered():
    r = client.post(
        "/activities/Chess Club/unregister", params={"email": "not@mergington.edu"}
    )
    assert r.status_code == 404
