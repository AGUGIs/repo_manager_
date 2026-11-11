-- ПР7: реляционная модель менеджера репозиториев.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    username TEXT NOT NULL UNIQUE CHECK (length(trim(username)) > 0),
    full_name TEXT NOT NULL,
    email TEXT
);
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    title TEXT NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    opened_on TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS repositories (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    project_id INTEGER NOT NULL REFERENCES projects(id),
    name TEXT NOT NULL,
    clone_url TEXT NOT NULL,
    private INTEGER NOT NULL DEFAULT 0 CHECK (private IN (0, 1))
);
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    repo_id INTEGER NOT NULL REFERENCES repositories(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    role TEXT NOT NULL CHECK (length(trim(role)) > 0),
    is_revoked INTEGER NOT NULL DEFAULT 0 CHECK (is_revoked IN (0, 1))
);
-- Отозванные записи сохраняются; повторный активный доступ запрещён.
CREATE UNIQUE INDEX IF NOT EXISTS members_active_unique
    ON members(repo_id, user_id) WHERE is_revoked = 0;
CREATE INDEX IF NOT EXISTS projects_owner ON projects(owner_id);
CREATE INDEX IF NOT EXISTS repositories_project ON repositories(project_id);
CREATE INDEX IF NOT EXISTS members_user ON members(user_id);
