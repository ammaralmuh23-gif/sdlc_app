import sqlite3
import os
from config import Config

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'sdlc_manager.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(sql, params=None, fetch=False):
    conn = None
    try:
        conn = get_connection()
        sql = sql.replace('%s', '?')
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        
        if fetch:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        conn.commit()
        return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
    except Exception as e:
        if conn:
            conn.rollback()
        raise RuntimeError(f"DB Error: {e}")
    finally:
        if conn:
            conn.close()

def execute_one(sql, params=None):
    rows = execute_query(sql, params, fetch=True)
    return rows[0] if rows else None
