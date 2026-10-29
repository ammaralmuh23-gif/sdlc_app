"""
models/audit.py — تسجيل النشاطات
المتطلبات: FR-11, FR-12, BR-03 (Append-only — لا حذف/تعديل)
"""
from models.db import execute_query


def log_action(action, entity_type, entity_id=None, details=None):
    """
    يسجل عملية في audit_log.

    Args:
        action (str): اسم العملية (CREATE_PROJECT, UPDATE_PHASE, ...)
        entity_type (str): نوع الكيان (project, phase, requirement)
        entity_id (int|None): رقم الكيان
        details (str|None): تفاصيل إضافية للقراءة البشرية
    """
    execute_query(
        """
        INSERT INTO audit_log (action, entity_type, entity_id, details)
        VALUES (%s, %s, %s, %s)
        """,
        (action, entity_type, entity_id, details)
    )


def get_recent_logs(limit=100):
    """
    يرجع آخر N نشاط مرتبة تنازلياً بالتاريخ — FR-12.
    limit يُمرَّر كـ parameterized query (آمن).
    """
    return execute_query(
        "SELECT * FROM audit_log ORDER BY created_at ASC LIMIT %s",
        (limit,),
        fetch=True
    )
