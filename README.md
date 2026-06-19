# GitHub REST API — Automated Test Suite

![CI](https://github.com/Michael-QA-Labs/github-api-tests/actions/workflows/test.yml/badge.svg)

Automated API test suite for the GitHub REST API built with Python and pytest. Independent portfolio project demonstrating backend API automation across multiple endpoints and resource types.

## What this tests

| Endpoint | Methods | Coverage |
|---|---|---|
| `/user` | GET | Auth validation, schema, response time |
| `/users/:username` | GET | Public lookup, 404 handling |
| `/user/repos` | GET, POST, DELETE | CRUD lifecycle, duplicate handling |
| `/gists` | POST, GET, DELETE | CRUD lifecycle, privacy, cleanup |
| `/rate_limit` | GET | SLA monitoring |

## Test strategy

Tests are organized into three categories:

- **smoke** — happy-path validation, run first
- **regression** — field validation, schema checks, behavioral assertions
- **negative** — 404s, 422s, auth failures, deleted resource access

Every test asserts on status code, response body schema, and response time under 3 seconds.

## Project structure

\`\`\`
github-api-tests/
├── .github/workflows/test.yml
├── config/settings.py
├── tests/
│   ├── test_user.py
│   ├── test_repos.py
│   └── test_gists.py
├── utils/api_client.py
├── conftest.py
├── pytest.ini
└── requirements.txt
\`\`\`

## Run locally

\`\`\`bash
git clone https://github.com/Michael-QA-Labs/github-api-tests.git
cd github-api-tests
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "GITHUB_TOKEN=your_ghp_token" > .env
echo "GITHUB_USERNAME=your_username" >> .env
pytest
\`\`\`

## Tech stack

Python 3.11 · pytest · requests · jsonschema · GitHub Actions · python-dotenv

## Author

**Michael Garcia** — QA Engineer, Backend API Automation
[LinkedIn](https://linkedin.com/in/michael-garcia03) · [GitHub](https://github.com/Michael-QA-Labs)
