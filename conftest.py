import uuid
import pytest
from utils.api_client import GitHubAPI
from config.settings import GITHUB_USERNAME


def unique_repo_name() -> str:
    """Generate a unique repo name so tests never collide."""
    return "test-repo-" + uuid.uuid4().hex[:8]


def unique_gist_description() -> str:
    return "test-gist-" + uuid.uuid4().hex[:8]


@pytest.fixture(scope="function")
def api():
    """Fresh GitHubAPI client for each test."""
    return GitHubAPI()


@pytest.fixture(scope="function")
def new_repo(api):
    """
    Create a repo before the test, yield its name,
    delete it after — even if the test fails.
    """
    name = unique_repo_name()
    response = api.create_repo(name, private=True, description="Automated test repo — safe to delete")
    assert response.status_code == 201, (
        f"Fixture setup failed — could not create repo. "
        f"Status: {response.status_code}, Body: {response.text}"
    )
    yield name
    api.delete_repo(GITHUB_USERNAME, name)


@pytest.fixture(scope="function")
def new_gist(api):
    """
    Create a gist before the test, yield its id,
    delete it after — even if the test fails.
    """
    response = api.create_gist(
        description="Automated test gist — safe to delete",
        filename="test.txt",
        content="This is a test gist created by the automated test suite.",
        public=False
    )
    assert response.status_code == 201, (
        f"Fixture setup failed — could not create gist. "
        f"Status: {response.status_code}, Body: {response.text}"
    )
    gist_id = response.json()["id"]
    yield gist_id
    api.delete_gist(gist_id)
