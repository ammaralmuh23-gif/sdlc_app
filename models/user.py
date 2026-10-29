"""
models/user.py — إدارة المستخدمين
FR-14..FR-20, NFR-10
"""
import bcrypt
from flask_login import UserMixin
from models.db import execute_query, execute_one


# ============================================================
# تشفير كلمة السر (NFR-10)
# ============================================================
def hash_password(plain_password):
    """يشفّر كلمة السر باستخدام bcrypt."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password, hashed_password):
    """يتحقق من كلمة السر مقابل الهاش."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, AttributeError):
        return False


# ============================================================
# كلاس User (متوافق مع Flask-Login)
# ============================================================
class User(UserMixin):
    """يكيّف dict المستخدم لـ Flask-Login."""

    def __init__(self, data):
        self.id = data["id"]
        self.username = data["username"]
        self.role = data["role"]
        self.is_active_flag = data["is_active"]
        self._password_hash = data["password"]

    @property
    def is_active(self):
        """Flask-Login يستخدمها لمعرفة إن كان الحساب نشطاً."""
        return bool(self.is_active_flag)

    @property
    def is_admin(self):
        """هل هذا المستخدم مدير؟"""
        return self.role == "admin"


# ============================================================
# CRUD المستخدمين
# ============================================================
def create_user(username, plain_password, role="user"):
    """ينشئ مستخدماً جديداً — FR-14."""
    existing = get_user_by_username(username)
    if existing:
        return None

    password_hash = hash_password(plain_password)
    return execute_query(
        "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
        (username, password_hash, role),
    )


def get_user_by_username(username):
    """يبحث عن مستخدم بـ username."""
    row = execute_one("SELECT * FROM users WHERE username = %s", (username,))
    return User(row) if row else None


def get_user(user_id):
    """يجلب مستخدماً بـ ID (يستخدمه Flask-Login)."""
    row = execute_one("SELECT * FROM users WHERE id = %s", (user_id,))
    return User(row) if row else None


def get_all_users():
    """كل المستخدمين — FR-19 (Admin only)."""
    return execute_query("SELECT * FROM users ORDER BY id ASC", fetch=True)


def toggle_user_active(user_id):
    """يفعّل/يعطّل حساب مستخدم — FR-20."""
    execute_query(
        "UPDATE users SET is_active = NOT is_active WHERE id = %s",
        (user_id,)
    )


def count_users():
    """عدد المستخدمين (نستخدمه لمعرفة أول مستخدم = admin)."""
    row = execute_one("SELECT COUNT(*) AS total FROM users")
    return row["total"] if row else 0
