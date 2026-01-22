PRAGMA foreign_keys = OFF;
DELETE FROM analysis_file_classes;
DELETE FROM analysis_files;
DELETE FROM repo_commits;
DELETE FROM repo_contributors;
DELETE FROM analyses;
PRAGMA foreign_keys = ON;
INSERT INTO analyses (
        id,
        name,
        status,
        origin_id,
        repo_url,
        repo_name,
        repo_owner_login,
        repo_created_at,
        repo_last_update,
        estimated_hours
    )
VALUES (
        1,
        'pycefr_testing',
        'completed',
        2,
        'https://github.com/PepeM112/pycefr',
        'pycefr',
        'PepeM112',
        '2024-05-02 10:26:27',
        '2026-01-06 17:03:47',
        73.5
    );
INSERT INTO analysis_files (id, analysis_id, filename)
VALUES (1, 1, 'backend/constants/analysis_rules.py');
INSERT INTO analysis_file_classes (file_id, class_id, level, instances)
VALUES (1, 7, 2, 90),
    (1, 8, 3, 1),
    (1, 15, 1, 1),
    (1, 26, 1, 2),
    (1, 43, 2, 2),
    (1, 49, 2, 4),
    (1, 54, 1, 3),
    (1, 65, 4, 1);
INSERT INTO analysis_files (id, analysis_id, filename)
VALUES (2, 1, 'backend/models/schemas/class_model.py');
INSERT INTO analysis_file_classes (file_id, class_id, level, instances)
VALUES (2, 23, 1, 91),
    (2, 54, 1, 3),
    (2, 65, 4, 2);
INSERT INTO analysis_files (id, analysis_id, filename)
VALUES (3, 1, 'backend/db/db_utils.py');
INSERT INTO analysis_file_classes (file_id, class_id, level, instances)
VALUES (3, 1, 1, 3),
    (3, 15, 1, 14),
    (3, 23, 1, 29),
    (3, 49, 2, 13),
    (3, 88, 3, 2);
INSERT INTO analysis_files (id, analysis_id, filename)
VALUES (4, 1, 'backend/main.py');
INSERT INTO analysis_file_classes (file_id, class_id, level, instances)
VALUES (4, 1, 1, 3),
    (4, 7, 2, 1),
    (4, 54, 1, 3);
INSERT INTO repo_commits (
        analysis_id,
        username,
        github_user,
        loc,
        commits,
        estimated_hours,
        total_files_modified
    )
VALUES (1, 'anapgh', 'anapgh', 21355, 227, 37.77, 32),
    (1, 'GitHub', 'anapgh', 27419, 26, 4.2, 150),
    (1, 'PepeM112', 'PepeM112', 3513, 9, 2.91, 28);
INSERT INTO repo_contributors (
        analysis_id,
        name,
        github_user,
        avatar,
        profile_url,
        contributions
    )
VALUES (
        1,
        'anapgh',
        'anapgh',
        'https://avatars.githubusercontent.com/u/60195957?v=4',
        'https://github.com/anapgh',
        246
    ),
    (
        1,
        'PepeM112',
        'PepeM112',
        'https://avatars.githubusercontent.com/u/129164725?v=4',
        'https://github.com/PepeM112',
        97
    );