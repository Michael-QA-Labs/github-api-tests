import time
import pytest
from jsonschema import validate
from utils.api_client import GitHubAPI, assert_response_time
from config.settings import GITHUB_USERNAME

GIST_SCHEMA = {
    "type": "object",
    "required": ["id", "description", "public", "owner", "files"],
    "properties": {
        "id": {"type": "string"},
        "description": {"type": "string"},
        "public": {"type": "boolean"},
        "owner": {"type": "object"},
        "files": {"type": "object"}
    }
}


# ---------------------------------------------------------------------------
# Smoke
# ---------------------------------------------------------------------------

@pytest.mark.smoke
def test_create_gist_returns_201(api, new_gist):
    """new_gist fixture creates it — verify it exists."""
    start = time.time()
    r = api.get_gist(new_gist)
    assert_response_time(time.time() - start)
    assert r.status_code == 200
    validate(instance=r.json(), schema=GIST_SCHEMA)


@pytest.mark.smoke
def test_delete_gist_returns_204(api):
    """Full lifecycle — create then delete."""
    create = api.create_gist(
        description="delete lifecycle test",
        filename="delete_test.txt",
        content="delete me",
        public=False
    )
    assert create.status_code == 201
    gist_id = create.json()["id"]

    start = time.time()
    r = api.delete_gist(gist_id)
    assert_response_time(time.time() - start)
    assert r.status_code == 204


# ---------------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------------

@pytest.mark.regression
def test_created_gist_is_private(api, new_gist):
    r = api.get_gist(new_gist)
    assert r.json()["public"] is False


@pytest.mark.regression
def test_created_gist_owner_matches_username(api, new_gist):
    r = api.get_gist(new_gist)
    assert r.json()["owner"]["login"] == GITHUB_USERNAME


@pytest.mark.regression
def test_created_gist_contains_expected_file(api, new_gist):
    r = api.get_gist(new_gist)
    assert "test.txt" in r.json()["files"]


@pytest.mark.regression
def test_created_gist_has_correct_description(api):
    description = "regression-test-gist"
    create = api.create_gist(
        description=description,
        filename="reg.txt",
        content="regression test content",
        public=False
    )
    assert create.status_code == 201
    gist_id = create.json()["id"]

    r = api.get_gist(gist_id)
    assert r.json()["description"] == description

    api.delete_gist(gist_id)


# ---------------------------------------------------------------------------
# Negative
# ---------------------------------------------------------------------------

@pytest.mark.negative
def test_get_nonexistent_gist_returns_404(api):
    start = time.time()
    r = api.get_gist("this-gist-does-not-exist-000000")
    assert_response_time(time.time() - start)
    assert r.status_code == 404


@pytest.mark.negative
def test_delete_nonexistent_gist_returns_404(api):
    start = time.time()
    r = api.delete_gist("this-gist-does-not-exist-000000")
    assert_response_time(time.time() - start)
    assert r.status_code == 404


@pytest.mark.negative
def test_deleted_gist_is_no_longer_accessible(api):
    """Verify delete actually removes the resource."""
    create = api.create_gist(
        description="to be deleted",
        filename="gone.txt",
        content="this will be deleted",
        public=False
    )
    gist_id = create.json()["id"]
    api.delete_gist(gist_id)

    r = api.get_gist(gist_id)
    assert r.status_code == 404, (
        f"Deleted gist should return 404, got {r.status_code}"
    )
