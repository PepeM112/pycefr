INSERT OR REPLACE INTO analyses (name, origin_id, total_hours, created_at)
VALUES ('test_analysis', 2, 5.5, '2026-01-20 10:00:00');

INSERT OR REPLACE INTO analysis_class (analysis_id, class_id, instances) VALUES (1, 7, 90);
INSERT OR REPLACE INTO analysis_class (analysis_id, class_id, instances) VALUES (1, 8, 1);
INSERT OR REPLACE INTO analysis_class (analysis_id, class_id, instances) VALUES (1, 23, 91);
INSERT OR REPLACE INTO analysis_class (analysis_id, class_id, instances) VALUES (1, 54, 3);
INSERT OR REPLACE INTO analysis_class (analysis_id, class_id, instances) VALUES (1, 65, 2);