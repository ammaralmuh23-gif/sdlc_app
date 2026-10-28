"""
routes/admin.py — إدارة المستخدمين (Admin only)
FR-19, FR-20
"""
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from models.user import get_all_users, toggle_user_active, get_user
from models.audit import log_action

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/users")
@login_required
def list_users():
    """FR-19: عرض كل المستخدمين (Admin only)"""
    if not current_user.is_admin:
        flash("هذه الصفحة للمسؤول فقط", "error")
        return redirect(url_for("dashboard.index"))

    users = get_all_users()
    return render_template("admin/users.html", users=users)


@bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
def toggle_user(user_id):
    """FR-20: تعطيل/تفعيل حساب مستخدم"""
    if not current_user.is_admin:
        flash("هذه العملية للمسؤول فقط", "error")
        return redirect(url_for("dashboard.index"))

    if user_id == current_user.id:
        flash("لا يمكنك تعطيل حسابك الخاص", "error")
        return redirect(url_for("admin.list_users"))

    target = get_user(user_id)
    if not target:
        flash("المستخدم غير موجود", "error")
        return redirect(url_for("admin.list_users"))

    toggle_user_active(user_id)
    log_action("TOGGLE_USER", "user", user_id, target.username)
    flash(f"تم تغيير حالة المستخدم {target.username}", "success")
    return redirect(url_for("admin.list_users"))