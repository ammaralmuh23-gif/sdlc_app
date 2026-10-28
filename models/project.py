"""
models/project.py — CRUD للمشاريع (v2.0 مع user_id)
"""
from models.db import execute_query, execute_one

def get_all_projects(user_id=None, is_admin=False):
    if is_admin:
        return execute_query("SELECT * FROM projects ORDER BY created_at DESC", fetch=True)
    return execute_query("SELECT * FROM projects WHERE user_id = %s ORDER BY created_at DESC", (user_id,), fetch=True)

def get_project(project_id, user_id=None, is_admin=False):
    if is_admin:
        return execute_one("SELECT * FROM projects WHERE id = %s", (project_id,))
    return execute_one("SELECT * FROM projects WHERE id = %s AND user_id = %s", (project_id, user_id))

def create_project(name, description, start_date, user_id):
    return execute_query(
        "INSERT INTO projects (name, description, start_date, user_id) VALUES (%s, %s, %s, %s)",
        (name, description, start_date, user_id)
    )

def update_project(project_id, name, description, start_date, status):
    execute_query(
        "UPDATE projects SET name = %s, description = %s, start_date = %s, status = %s WHERE id = %s",
        (name, description, start_date, status, project_id)
    )

def delete_project(project_id):
    execute_query("DELETE FROM projects WHERE id = %s", (project_id,))

def count_projects(user_id=None, is_admin=False):
    if is_admin:
        row = execute_one("SELECT COUNT(*) AS total FROM projects")
    else:
        row = execute_one("SELECT COUNT(*) AS total FROM projects WHERE user_id = %s", (user_id,))
    return row["total"] if row else 0

def count_active_projects(user_id=None, is_admin=False):
    if is_admin:
        row = execute_one("SELECT COUNT(*) AS total FROM projects WHERE status = 'active'")
    else:
        row = execute_one("SELECT COUNT(*) AS total FROM projects WHERE status = 'active' AND user_id = %s", (user_id,))
    return row["total"] if row else 0