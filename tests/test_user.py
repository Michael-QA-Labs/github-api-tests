import time
import pytest
from jsonschema import validate
from utils.api_client import GitHubAPI, assert_response_time
from config.settings import GITHUB_USERNAME

api = GitHubAPI()

USER_SCHEMA = {
    "type": "object",
    "required": ["login", "id", "type", "public_repos", "followers", "following"],
    "properties": {
        "login": {"type": "string"},
        "id": {"type": "integer"},
        "type": {"type": "string"},
        "public_repos": {"type": "integer"},
        "followers": {"type": "integer"},
        "following": {"type": "integer"}
    }
}

RATE_LIMIT_SCHEMA = {
    "type": "object",
    "required": ["resources", "rate"],
    "properties": {
        "resources": {"type": "object"},
        "rate": {
            "type": "object",
            "required": ["limit", "remaining", "reset"],
            "properties": {
                "limit": {"type": "integer"},
                "remaining": {"type": "integer"},
                "reset": {"type": "integer"}
            }
        }
    }
}


# ---------------------------------------------------------------------------
# Smoke
# ---------------------------------------------------------------------------

@pytest.mark.smoke
def test_get_authenticated_user_returns_200():
    start = time.time()
    r = api.get_authenticated_user()
    assert_response_time(time.time() - start)
    assert r.status_code == 200
    validate(instance=r.json(), schema=USER_SCHEMA)


@pytest.mark.smoke
def test_authenticated_user_login_matches_username():
    r = api.get_authenticated_user()
    assert r.json()["login"] == GITHUB_USERNAME, (
        f"Expected login '{GITHUB_USERNAME}', got '{r.json()['login']}'"
    )


@pytest.mark.smoke
def test_rate_limit_returns_200():
    start = time.time()
    r = api.get_rate_limit()
    assert_response_time(time.time() - start)
    assert r.status_code == 200
    validate(instance=r.json(), schema=RATE_LIMIT_SCHEMA)


# ---------------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------------

@pytest.mark.regression
def test_rate_limit_has_remaining_requests():
    r = api.get_rate_limit()
    remaining = r.json()["rate"]["remaining"]
    assert remaining > 0, f"Rate limit exhausted — {remaining} requests remaining"


@pytest.mark.regression
def test_get_public_user_returns_200():
    """Public user lookup — no auth needed but we send it anyway."""
    start = time.time()
    r = api.get_user(GITHUB_USERNAME)
    assert_response_time(time.time() - start)
    assert r.status_code == 200
    assert r.json()["login"] == GITHUB_USERNAME


@pytest.mark.regression
def test_authenticated_user_type_is_user():
    r = api.get_authenticated_user()
    assert r.json()["type"] == "User"


# ---------------------------------------------------------------------------
# Negative
# ---------------------------------------------------------------------------

@pytest.mark.negative
def test_get_nonexistent_user_returns_404():
    start = time.time()
    r = api.get_user("this-user-does-not-exist-xyzxyz123")
    assert_response_time(time.time() - start)
    assert r.status_code == 404


@pytest.mark.negative
def test_request_without_auth_returns_401():
    import requests
    start = time.time()
    r = requests.get("https://api.github.com/user")
    assert_response_time(time.time() - start)
    assert r.status_code == 401
