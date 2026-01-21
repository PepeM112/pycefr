-- Analysis
INSERT OR REPLACE INTO analyses (id, name, origin_id, total_hours, created_at)
VALUES (1, 'pycefr_analysis', 2, 70.59, '2026-01-20 10:00:00');

-- Analysis Classes
INSERT OR REPLACE INTO analysis_class (analysis_id, class_id, instances) VALUES (1, 7, 90);
INSERT OR REPLACE INTO analysis_class (analysis_id, class_id, instances) VALUES (1, 8, 1);
INSERT OR REPLACE INTO analysis_class (analysis_id, class_id, instances) VALUES (1, 23, 91);
INSERT OR REPLACE INTO analysis_class (analysis_id, class_id, instances) VALUES (1, 54, 3);
INSERT OR REPLACE INTO analysis_class (analysis_id, class_id, instances) VALUES (1, 65, 2);

-- Data
INSERT OR REPLACE INTO repo_general_info (
    analysis_id, name, url, description, created_at, last_updated_at,
    owner_name, owner_github_user, owner_avatar, owner_profile_url, owner_commits_count
) VALUES (
    1, 
    'pycefr', 
    'https://github.com/PepeM112/pycefr', 
    NULL, 
    '2024-05-02T10:26:27Z', 
    '2026-01-06T17:03:47Z',
    'PepeM112', 
    'PepeM112', 
    'https://avatars.githubusercontent.com/u/129164725?v=4', 
    'https://github.com/PepeM112', 
    NULL
);

-- Commits
INSERT OR REPLACE INTO repo_commit_stats (analysis_id, name, github_user, loc, commits_count, total_hours, total_files_modified)
VALUES 
    (1, 'anapgh', 'anapgh', 21355, 227, 37.77, 32),
    (1, 'GitHub', 'anapgh', 27419, 26, 4.2, 150),
    (1, 'Gregorio', 'gregoriorobles', 1107, 8, 2.29, 8),
    (1, 'PepeM112', 'PepeM112', 3513, 9, 2.91, 28),
    (1, 'jmatas', 'PepeM112', 20162, 81, 23.42, 59);

-- Contributors
INSERT OR REPLACE INTO repo_contributors (analysis_id, name, github_user, avatar, profile_url, contributions_count)
VALUES 
    (1, 'anapgh', 'anapgh', 'https://avatars.githubusercontent.com/u/60195957?v=4', 'https://github.com/anapgh', 246),
    (1, 'PepeM112', 'PepeM112', 'https://avatars.githubusercontent.com/u/129164725?v=4', 'https://github.com/PepeM112', 97),
    (1, 'gregoriorobles', 'gregoriorobles', 'https://avatars.githubusercontent.com/u/842692?v=4', 'https://github.com/gregoriorobles', 8);