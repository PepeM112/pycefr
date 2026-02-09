DROP TABLE IF EXISTS repo_contributors;
DROP TABLE IF EXISTS repo_commits;
DROP TABLE IF EXISTS analysis_file_classes;
DROP TABLE IF EXISTS analysis_files;
DROP TABLE IF EXISTS analyses;
DROP TABLE IF EXISTS class_model;
CREATE TABLE class_model (
    id INTEGER PRIMARY KEY,
    level INTEGER NOT NULL CHECK (level BETWEEN 0 AND 6)
);
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('in_progress', 'completed', 'failed')),
    origin TEXT NOT NULL CHECK (origin IN ('USER', 'GITHUB', 'LOCAL', 'UNKNOWN')),
    repo_url TEXT,
    repo_name TEXT,
    repo_description TEXT,
    repo_owner_name TEXT,
    repo_owner_login TEXT,
    repo_owner_avatar TEXT,
    repo_owner_profile_url TEXT,
    repo_created_at DATETIME,
    repo_last_update DATETIME,
    estimated_hours REAL DEFAULT 0.0,
    error_message TEXT,
    created_at DATETIME NOT NULL
);
CREATE TABLE analysis_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE,
    UNIQUE(analysis_id, filename)
);
CREATE TABLE analysis_file_classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    instances INTEGER DEFAULT 0,
    FOREIGN KEY (file_id) REFERENCES analysis_files(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES class_model(id)
);
CREATE TABLE repo_commits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    username TEXT,
    github_user TEXT,
    loc INTEGER DEFAULT 0,
    commits INTEGER DEFAULT 0,
    estimated_hours REAL DEFAULT 0.0,
    total_files_modified INTEGER DEFAULT 0,
    FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE
);
CREATE TABLE repo_contributors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    name TEXT,
    github_user TEXT NOT NULL,
    avatar TEXT,
    profile_url TEXT,
    contributions INTEGER DEFAULT 0,
    FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE
);
CREATE INDEX idx_analysis_status ON analyses(status);
CREATE INDEX idx_files_analysis_id ON analysis_files(analysis_id);
CREATE INDEX idx_classes_file_id ON analysis_file_classes(file_id);