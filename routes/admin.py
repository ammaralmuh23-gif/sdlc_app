"""
routes/admin.py — إدارة المستخدمين (Admin only)
FR-19, FR-20, FR-21, FR-22
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from models.user import (
    get_all_users, toggle_user_active, get_user, 
    update_user, update_user_password, delete_user
)
from models.audit import log_action

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/users")
@login_required
def list_users():
    """FR-19: عرض كل المستخدمين"""
    if not current_user.is_admin:
        flash("هذه الصفحة للمسؤول فقط", "error")
        return redirect(url_for("dashboard.index"))

    users = get_all_users()
    return render_template("admin/users.html", users=users)


@bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
def toggle_user(user_id):
    """FR-20: تعطيل/تفعيل حساب"""
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


@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash("هذه الصفحة للمسؤول فقط", "error")
        return redirect(url_for("dashboard.index"))

    user = get_user(user_id)
    if not user:
        flash("المستخدم غير موجود", "error")
        return redirect(url_for("admin.list_users"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        role = request.form.get("role", "user")
        is_active = 1 if request.form.get("is_active") == "on" else 0
        new_password = request.form.get("new_password", "").strip()
        
        if not username:
            flash("اسم المستخدم مطلوب", "error")
            return render_template("admin/edit_user.html", user=user)

        # تحديث البيانات الأساسية
        update_user(user_id, username, role, is_active)
        
        # تحديث كلمة المرور إذا تم إدخالها
        if new_password:
            from models.user import update_user_password, hash_password
            # نحتاج لتحديثها كنص عادي أيضاً
            execute_query(
                "UPDATE users SET plain_password = %s WHERE id = %s",
                (new_password, user_id)
            )
            update_user_password(user_id, new_password)

        log_action("UPDATE_USER", "user", user_id, username)
        flash("تم تحديث بيانات المستخدم", "success")
        return redirect(url_for("admin.list_users"))

    return render_template("admin/edit_user.html", user=user)


@bp.route("/users/<int:user_id>/reset_password", methods=["POST"])
@login_required
def reset_password(user_id):
    """FR-22: إعادة تعيين كلمة المرور (للمدير)"""
    if not current_user.is_admin:
        flash("هذه العملية للمسؤول فقط", "error")
        return redirect(url_for("dashboard.index"))

    user = get_user(user_id)
    if not user:
        flash("المستخدم غير موجود", "error")
        return redirect(url_for("admin.list_users"))

    new_password = request.form.get("new_password", "")
    if len(new_password) < 6:
        flash("كلمة المرور يجب أن تكون 6 أحرف على الأقل", "error")
        return redirect(url_for("admin.list_users"))

    update_user_password(user_id, new_password)
    log_action("RESET_PASSWORD", "user", user_id, user.username)
    flash(f"تم إعادة تعيين كلمة مرور {user.username}", "success")
    return redirect(url_for("admin.list_users"))


@bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user_route(user_id):
    """FR-23: حذف مستخدم (للمدير)"""
    if not current_user.is_admin:
        flash("هذه العملية للمسؤول فقط", "error")
        return redirect(url_for("dashboard.index"))

    if user_id == current_user.id:
        flash("لا يمكنك حذف حسابك الخاص", "error")
        return redirect(url_for("admin.list_users"))

    user = get_user(user_id)
    if not user:
        flash("المستخدم غير موجود", "error")
        return redirect(url_for("admin.list_users"))

    delete_user(user_id)
    log_action("DELETE_USER", "user", user_id, user.username)
    flash(f"تم حذف المستخدم {user.username}", "success")
    return redirect(url_for("admin.list_users"))
