"""
routes/auth.py — تسجيل/دخول/خروج
FR-14, FR-15, FR-16, NFR-10, NFR-11
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import (
    create_user, get_user_by_username, verify_password, count_users
)
from models.audit import log_action

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    """FR-14: إنشاء حساب جديد"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        # التحقق من المدخلات
        if not username or len(username) < 3:
            flash("اسم المستخدم يجب أن يكون 3 أحرف على الأقل", "error")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("كلمة السر يجب أن تكون 6 أحرف على الأقل", "error")
            return render_template("auth/register.html")

        if password != confirm:
            flash("كلمتا السر غير متطابقتين", "error")
            return render_template("auth/register.html")

        # أول مستخدم يصبح Admin تلقائياً
        role = "admin" if count_users() == 0 else "user"

        user_id = create_user(username, password, role)
        if not user_id:
            flash("اسم المستخدم مستخدم بالفعل", "error")
            return render_template("auth/register.html")

        log_action("CREATE_USER", "user", user_id, username)
        flash("تم إنشاء الحساب — سجّل الدخول الآن", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """FR-15: تسجيل الدخول"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)

        # التحقق من المستخدم وكلمة السر
        if not user or not verify_password(password, user._password_hash):
            flash("اسم المستخدم أو كلمة السر غير صحيحة", "error")
            return render_template("auth/login.html")

        if not user.is_active:
            flash("حسابك معطّل — راجع المسؤول", "error")
            return render_template("auth/login.html")

        login_user(user)
        log_action("LOGIN", "user", user.id, user.username)
        flash(f"أهلاً {user.username}", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html")


@bp.route("/logout")
@login_required
def logout():
    """FR-16: تسجيل الخروج"""
    log_action("LOGOUT", "user", current_user.id, current_user.username)
    logout_user()
    flash("تم تسجيل الخروج", "success")
    return redirect(url_for("auth.login"))