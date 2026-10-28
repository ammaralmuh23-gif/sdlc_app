"""
routes/dashboard.py — لوحة التحكم
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.project import count_projects, count_active_projects
from models.phase import count_completed_phases
from models.requirement import count_open_requirements

bp = Blueprint("dashboard", __name__)

@bp.route("/")
@login_required  # ← هذا السطر يمنع الدخول بدون حساب
def index():
    is_admin = current_user.is_admin
    uid = current_user.id

    stats = {
        "total_projects": count_projects(uid, is_admin),
        "active_projects": count_active_projects(uid, is_admin),
        "completed_phases": count_completed_phases(uid, is_admin),
        "open_requirements": count_open_requirements(uid, is_admin),
    }
    return render_template("dashboard.html", stats=stats)