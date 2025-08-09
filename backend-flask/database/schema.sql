CREATE TABLE level (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE origin (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE class (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    level_id INTEGER NOT NULL,
    FOREIGN KEY (level_id) REFERENCES level(id)
);

CREATE TABLE analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    origin_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (origin_id) REFERENCES origin(id)
);

CREATE TABLE analysis_class (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    instances INTEGER NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analysis(id),
    FOREIGN KEY (class_id) REFERENCES class(id),
    UNIQUE (analysis_id, class_id)
);