CREATE TABLE IF NOT EXISTS origins (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    origin_id INTEGER NOT NULL,
    total_hours REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (origin_id) REFERENCES origins (id)
);

CREATE TABLE IF NOT EXISTS analysis_class (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    instances INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE
    UNIQUE (analysis_id, class_id)
);

CREATE TABLE IF NOT EXISTS repo_general_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    created_at TEXT,
    last_updated_at TEXT,
    owner_name TEXT,
    owner_github_user TEXT NOT NULL,
    owner_avatar TEXT,
    owner_profile_url TEXT,
    owner_commits_count INTEGER,
    FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS repo_commit_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    name TEXT,
    github_user TEXT NOT NULL,
    loc INTEGER NOT NULL,
    commits_count INTEGER NOT NULL,
    total_hours REAL NOT NULL,
    total_files_modified INTEGER NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS repo_contributors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    name TEXT,
    github_user TEXT NOT NULL,
    avatar TEXT,
    profile_url TEXT,
    contributions_count INTEGER NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE
);

-- Initial Data for Origins (matching Origin Enum)
INSERT OR IGNORE INTO origins (id, name) VALUES (0, 'UNKNOWN');
INSERT OR IGNORE INTO origins (id, name) VALUES (1, 'USER');
INSERT OR IGNORE INTO origins (id, name) VALUES (2, 'GITHUB');
INSERT OR IGNORE INTO origins (id, name) VALUES (3, 'LOCAL');