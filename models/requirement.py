"""
models/requirement.py — CRUD للمتطلبات
المتطلبات: FR-07, FR-08, FR-01
"""
from models.db import execute_query, execute_one


# ============================================================
# قراءة
# ============================================================

def get_requirements_by_project(project_id):
    """يرجع متطلبات مشروع مرتبة بالأحدث — FR-09"""
    return execute_query(
        """
        SELECT * FROM requirements
        WHERE project_id = %s
       ORDER BY id ASC
        """,
        (project_id,),
        fetch=True
    )


def get_requirement(requirement_id):
    """يرجع متطلباً واحداً أو None — FR-08"""
    return execute_one(
        "SELECT * FROM requirements WHERE id = %s",
        (requirement_id,)
    )


# ============================================================
# كتابة
# ============================================================

def create_requirement(project_id, title, description, status="open"):
    """
    ينشئ متطلباً جديداً ويعيد ID — FR-07.
    الحالة الافتراضية 'open'.
    """
    return execute_query(
        """
        INSERT INTO requirements (project_id, title, description, status)
        VALUES (%s, %s, %s, %s)
        """,
        (project_id, title, description, status)
    )


def update_requirement(requirement_id, title, description, status):
    """يحدّث متطلباً — FR-08"""
    execute_query(
        """
        UPDATE requirements
        SET title = %s, description = %s, status = %s
        WHERE id = %s
        """,
        (title, description, status, requirement_id)
    )


def delete_requirement(requirement_id):
    """يحذف متطلباً — FR-08"""
    execute_query(
        "DELETE FROM requirements WHERE id = %s",
        (requirement_id,)
    )


# ============================================================
# إحصائيات (v2.0)
# ============================================================

def count_open_requirements(user_id=None, is_admin=False):
    """عدد المتطلبات المفتوحة — FR-01 (يُحسب حسب المستخدم)"""
    if is_admin:
        row = execute_one(
            "SELECT COUNT(*) AS total FROM requirements WHERE status = 'open'"
        )
    else:
        row = execute_one(
            """
            SELECT COUNT(*) AS total FROM requirements r
            JOIN projects pr ON r.project_id = pr.id
            WHERE r.status = 'open' AND pr.user_id = %s
            """,
            (user_id,)
        )
    return row["total"] if row else 0
