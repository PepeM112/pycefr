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

-- Initial Data for Origins (matching Origin Enum)
INSERT OR IGNORE INTO origins (id, name) VALUES (0, 'UNKNOWN');
INSERT OR IGNORE INTO origins (id, name) VALUES (1, 'USER');
INSERT OR IGNORE INTO origins (id, name) VALUES (2, 'GITHUB');
INSERT OR IGNORE INTO origins (id, name) VALUES (3, 'LOCAL');