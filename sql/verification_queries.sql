-- Urban Scooter / GitHub API Test Suite
-- Database-layer verification queries
-- Simulates post-API-call DB checks used in production QA automation
-- Database: SQLite (mirrors PostgreSQL patterns used in real environments)

-- ── 1. Confirm authenticated user was written correctly ──────────────────
SELECT id, login, type, public_repos, followers
FROM users
WHERE login = 'Michael-QA-Labs';

-- ── 2. Count total repos seeded from API ────────────────────────────────
SELECT COUNT(*) AS total_repos
FROM repos;

-- ── 3. Public vs private breakdown ──────────────────────────────────────
SELECT
    CASE WHEN private = 1 THEN 'Private' ELSE 'Public' END AS visibility,
    COUNT(*) AS count
FROM repos
GROUP BY private;

-- ── 4. Verify portfolio repos exist and are public ───────────────────────
SELECT name, private, html_url
FROM repos
WHERE name LIKE '%api-tests%'
ORDER BY name;

-- ── 5. Data integrity check — owner must match authenticated user ────────
SELECT name, owner_login
FROM repos
WHERE owner_login != (SELECT login FROM users LIMIT 1);

-- ── 6. Find repos missing descriptions (documentation gap) ───────────────
SELECT name
FROM repos
WHERE description IS NULL OR description = '';

-- ── 7. Join users and repos — full ownership report ─────────────────────
SELECT
    u.login AS owner,
    r.name AS repo_name,
    CASE WHEN r.private = 1 THEN 'Private' ELSE 'Public' END AS visibility,
    r.description
FROM repos r
JOIN users u ON r.owner_login = u.login
ORDER BY r.private DESC, r.name ASC;
