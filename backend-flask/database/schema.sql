CREATE TABLE class (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    level INTEGER NOT NULL
);

CREATE TABLE analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    origin INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
);

CREATE TABLE analysis_class (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    class INTEGER NOT NULL,
    instances INTEGER NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analysis(id),
    UNIQUE (analysis_id, class)
);