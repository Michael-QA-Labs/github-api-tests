import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "Michael-QA-Labs")

BASE_URL = "https://api.github.com"

# Endpoints
USER_ENDPOINT          = f"{BASE_URL}/user"
REPOS_ENDPOINT         = f"{BASE_URL}/user/repos"
GISTS_ENDPOINT         = f"{BASE_URL}/gists"
RATE_LIMIT_ENDPOINT    = f"{BASE_URL}/rate_limit"

# Auth header used by every request
AUTH_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

RESPONSE_TIME_LIMIT_SECONDS = 3.0
