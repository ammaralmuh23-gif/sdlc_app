"""
models/db.py — طبقة الاتصال بقاعدة البيانات
كل الاستعلامات تمر من هنا (AR-01: Routes لا تكتب SQL مباشرة)
الحماية: Parameterized Queries (NFR-02)
"""
import mysql.connector
from mysql.connector import Error
from config import Config


def get_connection():
    """
    يفتح اتصالاً جديداً بقاعدة البيانات.
    يُستدعى من execute_query() فقط — لا تستدعيه مباشرة من Routes.
    """
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset="utf8mb4",              # دعم العربية
        collation="utf8mb4_unicode_ci",
        autocommit=False,                # نتحكم بالـ commit يدوياً
    )


def execute_query(sql, params=None, fetch=False):
    """
    ينفذ استعلاماً بشكل آمن (Parameterized — NFR-02).

    Args:
        sql (str): الاستعلام مع %s للأماكن المتغيرة.
        params (tuple): القيم المقابلة لـ %s.
        fetch (bool): True → SELECT (يرجع صفوف)، False → INSERT/UPDATE/DELETE (commit).

    Returns:
        list[dict]: إذا fetch=True.
        int: lastrowid (INSERT) أو rowcount (UPDATE/DELETE).

    Raises:
        RuntimeError: عند أي خطأ في قاعدة البيانات (مع rollback تلقائي).
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)    # النتائج كـ dict
        cursor.execute(sql, params or ())

        if fetch:
            return cursor.fetchall()

        conn.commit()
        # INSERT → lastrowid، UPDATE/DELETE → rowcount
        return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    except Error as e:
        if conn:
            conn.rollback()
        raise RuntimeError(f"DB Error: {e}") from e

    finally:
        # إغلاق دائم — يمنع تسريب الاتصالات
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


def execute_one(sql, params=None):
    """
    يرجع صفاً واحداً فقط (أو None إذا لم يوجد).

    يستخدم للاستعلامات: SELECT ... WHERE id = %s
    """
    rows = execute_query(sql, params, fetch=True)
    return rows[0] if rows else None