import sqlite3
from typing import List, Dict, Optional

DATABASE_PATH = 'database/pycefr.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query: str, args: tuple = (), fetch_one: bool = False):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    
    if fetch_one:
        result = cursor.fetchone()
    else:
        result = cursor.fetchall()
    
    conn.commit()
    conn.close()
    return result

def get_levels() -> List[Dict]:
    query = "SELECT * FROM level"
    levels = execute_query(query)
    return [dict(level) for level in levels]

def get_origins() -> List[Dict]:
    query = "SELECT * FROM origin"
    origins = execute_query(query)
    return [dict(origin) for origin in origins]

def get_classes() -> List[Dict]:
    query = "SELECT c.id, c.name, l.name as level_name FROM class c JOIN level l ON c.level_id = l.id"
    classes = execute_query(query)
    return [dict(cls) for cls in classes]

def get_analyses() -> List[Dict]:
    query = """
    SELECT a.id, a.name, o.name as origin_name, a.created_at 
    FROM analysis a 
    JOIN origin o ON a.origin_id = o.id
    """
    analyses = execute_query(query)
    return [dict(analysis) for analysis in analyses]

def get_analysis_classes(analysis_id: int) -> List[Dict]:
    query = """
    SELECT ac.id, c.name as class_name, l.name as level_name, ac.instances
    FROM analysis_class ac
    JOIN class c ON ac.class_id = c.id
    JOIN level l ON c.level_id = l.id
    WHERE ac.analysis_id = ?
    """
    analysis_classes = execute_query(query, (analysis_id,))
    return [dict(ac) for ac in analysis_classes]

def create_analysis(name: str, origin_id: int, classes: List[Dict]) -> Optional[int]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insertar análisis
        cursor.execute(
            "INSERT INTO analysis (name, origin_id) VALUES (?, ?)",
            (name, origin_id)
        )
        analysis_id = cursor.lastrowid
        
        # Insertar clases del análisis
        for class_data in classes:
            cursor.execute(
                "INSERT INTO analysis_class (analysis_id, class_id, instances) VALUES (?, ?, ?)",
                (analysis_id, class_data['class_id'], class_data['instances']))
        
        conn.commit()
        return analysis_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()