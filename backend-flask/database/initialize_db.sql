INSERT INTO level (id, name) VALUES 
(1, 'A1'), (2, 'A2'), (3, 'B1'), 
(4, 'B2'), (5, 'C1'), (6, 'C2');

INSERT INTO origin (id, name) VALUES 
(1, 'repo'), (2, 'user'), (3, 'dir');

INSERT INTO class (id, name, level_id) VALUES
(1, 'Simple List', 1),
(2, 'Simple Tuple', 1),
(3, '2 Nested Tuple', 2),
(4, 'enumerate call function', 6);