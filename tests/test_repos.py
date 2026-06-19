import time
import pytest
from jsonschema import validate
from utils.api_client import GitHubAPI, assert_response_time
from config.settings import GITHUB_USERNAME

REPO_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "full_name", "private", "owner", "html_url"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "full_name": {"type": "string"},
        "private": {"type": "boolean"},
        "owner": {"type": "object"},
        "html_url": {"type": "string"}
    }
}

REPOS_LIST_SCHEMA = {
    "type": "array",
    "items": REPO_SCHEMA
}


# ---------------------------------------------------------------------------
# Smoke
# ---------------------------------------------------------------------------

@pytest.mark.smoke
def test_list_repos_returns_200(api):
    start = time.time()
    r = api.list_repos()
    assert_response_time(time.time() - start)
    assert r.status_code == 200
    validate(instance=r.json(), schema=REPOS_LIST_SCHEMA)


@pytest.mark.smoke
def test_create_repo_returns_201(api, new_repo):
    """new_repo fixture creates the repo — we just verify it exists."""
    start = time.time()
    r = api.get_repo(GITHUB_USERNAME, new_repo)
    assert_response_time(time.time() - start)
    assert r.status_code == 200
    validate(instance=r.json(), schema=REPO_SCHEMA)
    assert r.json()["name"] == new_repo


@pytest.mark.smoke
def test_delete_repo_returns_204(api):
    """Full lifecycle — create then delete."""
    name = "test-repo-delete-" + __import__('uuid').uuid4().hex[:6]
    create = api.create_repo(name, description="delete test")
    assert create.status_code == 201

    start = time.time()
    r = api.delete_repo(GITHUB_USERNAME, name)
    assert_response_time(time.time() - start)
    assert r.status_code == 204


# ---------------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------------

@pytest.mark.regression
def test_created_repo_owner_matches_username(api, new_repo):
    r = api.get_repo(GITHUB_USERNAME, new_repo)
    assert r.json()["owner"]["login"] == GITHUB_USERNAME


@pytest.mark.regression
def test_created_repo_is_public_by_default(api):
    """GitHub creates repos as public unless private=True is specified."""
    import uuid
    name = "test-repo-" + uuid.uuid4().hex[:6]
    api.create_repo(name, private=False)
    r = api.get_repo(GITHUB_USERNAME, name)
    assert r.json()["private"] is False
    api.delete_repo(GITHUB_USERNAME, name)


@pytest.mark.regression
def test_created_repo_has_correct_name(api, new_repo):
    r = api.get_repo(GITHUB_USERNAME, new_repo)
    assert r.json()["name"] == new_repo


@pytest.mark.regression
def test_list_repos_returns_list(api):
    r = api.list_repos()
    assert isinstance(r.json(), list)


@pytest.mark.regression
def test_created_repo_appears_in_list(api, new_repo):
    r = api.list_repos()
    repo_names = [repo["name"] for repo in r.json()]
    assert new_repo in repo_names, (
        f"Newly created repo '{new_repo}' not found in repo list"
    )


# ---------------------------------------------------------------------------
# Negative
# ---------------------------------------------------------------------------

@pytest.mark.negative
def test_get_nonexistent_repo_returns_404(api):
    start = time.time()
    r = api.get_repo(GITHUB_USERNAME, "this-repo-does-not-exist-xyzxyz")
    assert_response_time(time.time() - start)
    assert r.status_code == 404


@pytest.mark.negative
def test_create_repo_with_empty_name_returns_422(api):
    start = time.time()
    r = api.create_repo("")
    assert_response_time(time.time() - start)
    assert r.status_code == 422


@pytest.mark.negative
def test_delete_nonexistent_repo_returns_404(api):
    start = time.time()
    r = api.delete_repo(GITHUB_USERNAME, "repo-that-does-not-exist-xyzxyz")
    assert_response_time(time.time() - start)
    assert r.status_code == 404


@pytest.mark.negative
def test_create_duplicate_repo_returns_422(api, new_repo):
    """Creating a repo with the same name should be rejected."""
    start = time.time()
    r = api.create_repo(new_repo)
    assert_response_time(time.time() - start)
    assert r.status_code == 422, (
        f"Duplicate repo should return 422, got {r.status_code}. Body: {r.text}"
    )
