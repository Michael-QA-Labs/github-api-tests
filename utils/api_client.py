import time
import requests
from config.settings import AUTH_HEADERS, RESPONSE_TIME_LIMIT_SECONDS


class GitHubAPI:
    """
    Thin wrapper around the GitHub REST API.
    All tests call methods here — never raw requests directly.
    """

    def get_authenticated_user(self) -> requests.Response:
        return requests.get("https://api.github.com/user", headers=AUTH_HEADERS)

    def get_rate_limit(self) -> requests.Response:
        return requests.get("https://api.github.com/rate_limit", headers=AUTH_HEADERS)

    def list_repos(self) -> requests.Response:
        return requests.get("https://api.github.com/user/repos", headers=AUTH_HEADERS)

    def create_repo(self, name: str, private: bool = False, description: str = "") -> requests.Response:
        payload = {"name": name, "private": private, "description": description, "auto_init": False}
        return requests.post("https://api.github.com/user/repos", headers=AUTH_HEADERS, json=payload)

    def get_repo(self, owner: str, repo: str) -> requests.Response:
        return requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=AUTH_HEADERS)

    def delete_repo(self, owner: str, repo: str) -> requests.Response:
        return requests.delete(f"https://api.github.com/repos/{owner}/{repo}", headers=AUTH_HEADERS)

    def create_gist(self, description: str, filename: str, content: str, public: bool = False) -> requests.Response:
        payload = {
            "description": description,
            "public": public,
            "files": {filename: {"content": content}}
        }
        return requests.post("https://api.github.com/gists", headers=AUTH_HEADERS, json=payload)

    def get_gist(self, gist_id: str) -> requests.Response:
        return requests.get(f"https://api.github.com/gists/{gist_id}", headers=AUTH_HEADERS)

    def delete_gist(self, gist_id: str) -> requests.Response:
        return requests.delete(f"https://api.github.com/gists/{gist_id}", headers=AUTH_HEADERS)

    def get_user(self, username: str) -> requests.Response:
        return requests.get(f"https://api.github.com/users/{username}", headers=AUTH_HEADERS)


def assert_response_time(elapsed: float, limit: float = RESPONSE_TIME_LIMIT_SECONDS):
    """Enforce SLA on every request."""
    assert elapsed < limit, f"Response too slow: {elapsed:.2f}s (limit: {limit}s)"
