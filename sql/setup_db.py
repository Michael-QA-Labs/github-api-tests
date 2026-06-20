"""
Simulates the database-layer verification pattern used in real QA automation.
Fetches live data from the GitHub API, stores it in SQLite,
then runs integrity queries to verify the data matches API responses.

In production environments this same pattern queries a real PostgreSQL
or MySQL database directly after API calls to catch data integrity bugs.
"""

import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import GitHubAPI

DB_PATH = "sql/github_data.db"


def create_tables(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY,
            login       TEXT NOT NULL,
            type        TEXT,
            public_repos INTEGER,
            followers   INTEGER,
            following   INTEGER,
            created_at  TEXT
        );

        CREATE TABLE IF NOT EXISTS repos (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            full_name   TEXT,
            private     INTEGER,
            owner_login TEXT,
            html_url    TEXT,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS gists (
            id          TEXT PRIMARY KEY,
            description TEXT,
            public      INTEGER,
            owner_login TEXT,
            created_at  TEXT
        );
    """)
    conn.commit()
    print("Tables created.")


def seed_from_api(conn):
    api = GitHubAPI()

    # Seed user
    r = api.get_authenticated_user()
    if r.status_code == 200:
        u = r.json()
        conn.execute("""
            INSERT OR REPLACE INTO users
            (id, login, type, public_repos, followers, following, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (u["id"], u["login"], u["type"], u["public_repos"], u["followers"], u["following"], u.get("created_at")))
        print(f"Seeded user: {u['login']}")

    # Seed repos
    r = api.list_repos()
    if r.status_code == 200:
        for repo in r.json():
            conn.execute("""
                INSERT OR REPLACE INTO repos
                (id, name, full_name, private, owner_login, html_url, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (repo["id"], repo["name"], repo["full_name"], int(repo["private"]),
                  repo["owner"]["login"], repo["html_url"], repo.get("description")))
        print(f"Seeded {len(r.json())} repos.")

    conn.commit()


def run_verification_queries(conn):
    print("\n--- SQL Verification Queries ---\n")

    # Query 1 — user exists
    print("1. Authenticated user in database:")
    for row in conn.execute("SELECT id, login, type, public_repos, followers FROM users"):
        print(f"   id={row[0]}, login={row[1]}, type={row[2]}, public_repos={row[3]}, followers={row[4]}")

    # Query 2 — repo count
    print("\n2. Total repos in database:")
    count = conn.execute("SELECT COUNT(*) FROM repos").fetchone()[0]
    print(f"   {count} repos")

    # Query 3 — public vs private breakdown
    print("\n3. Public vs private repos:")
    for row in conn.execute("SELECT private, COUNT(*) as count FROM repos GROUP BY private"):
        label = "Private" if row[0] else "Public"
        print(f"   {label}: {row[1]}")

    # Query 4 — find portfolio repos
    print("\n4. Portfolio repos (containing 'api-tests'):")
    for row in conn.execute("SELECT name, private, html_url FROM repos WHERE name LIKE '%api-tests%'"):
        visibility = "private" if row[1] else "public"
        print(f"   {row[0]} ({visibility}) — {row[2]}")

    # Query 5 — verify owner consistency
    print("\n5. Repos where owner does not match authenticated user (data integrity check):")
    user = conn.execute("SELECT login FROM users LIMIT 1").fetchone()
    if user:
        mismatches = conn.execute(
            "SELECT name, owner_login FROM repos WHERE owner_login != ?", (user[0],)
        ).fetchall()
        if mismatches:
            for row in mismatches:
                print(f"   MISMATCH: {row[0]} owned by {row[1]}")
        else:
            print("   No mismatches — all repos owned by authenticated user.")

    # Query 6 — repos with no description
    print("\n6. Repos missing descriptions (documentation gap):")
    for row in conn.execute("SELECT name FROM repos WHERE description IS NULL OR description = ''"):
        print(f"   {row[0]}")


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    seed_from_api(conn)
    run_verification_queries(conn)
    conn.close()
    print("\nDone.")
