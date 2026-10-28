"""
models/phase.py — CRUD للمراحل + إنشاء المراحل الست تلقائياً
المتطلبات: FR-05, FR-06, BR-02
"""
from models.db import execute_query, execute_one


# BR-02: المراحل الست الثابتة لكل مشروع SDLC
DEFAULT_PHASES = [
    "Planning",
    "Requirements",
    "Design",
    "Implementation",
    "Testing",
    "Deployment",
]


# ============================================================
# إنشاء
# ============================================================

def create_default_phases(project_id):
    """
    ينشئ 6 مراحل SDLC لمشروع جديد — FR-05, BR-02.
    تُستدعى تلقائياً بعد create_project() في routes/projects.py.
    """
    for index, name in enumerate(DEFAULT_PHASES, start=1):
        execute_query(
            """
            INSERT INTO phases (project_id, name, status, order_index)
            VALUES (%s, %s, 'pending', %s)
            """,
            (project_id, name, index)
        )


# ============================================================
# قراءة
# ============================================================

def get_phases_by_project(project_id):
    """يرجع كل مراحل مشروع مرتبة — FR-09"""
    return execute_query(
        """
        SELECT * FROM phases
        WHERE project_id = %s
        ORDER BY order_index
        """,
        (project_id,),
        fetch=True
    )


def get_phase(phase_id):
    """يرجع مرحلة واحدة أو None — FR-06"""
    return execute_one(
        "SELECT * FROM phases WHERE id = %s",
        (phase_id,)
    )


# ============================================================
# تحديث
# ============================================================

def update_phase_status(phase_id, new_status):
    """
    يغيّر حالة مرحلة — FR-06.
    التحقق من صحة القيمة يتم في Route (VALID_STATUSES).
    """
    execute_query(
        "UPDATE phases SET status = %s WHERE id = %s",
        (new_status, phase_id)
    )


# ============================================================
# إحصائيات (v2.0)
# ============================================================

def count_completed_phases(user_id=None, is_admin=False):
    """عدد المراحل المكتملة — FR-01 (يُحسب حسب المستخدم)"""
    if is_admin:
        row = execute_one(
            "SELECT COUNT(*) AS total FROM phases WHERE status = 'completed'"
        )
    else:
        row = execute_one(
            """
            SELECT COUNT(*) AS total FROM phases p
            JOIN projects pr ON p.project_id = pr.id
            WHERE p.status = 'completed' AND pr.user_id = %s
            """,
            (user_id,)
        )
    return row["total"] if row else 0