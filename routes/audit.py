"""
routes/audit.py — سجل النشاطات
"""
from flask import Blueprint, render_template
from flask_login import login_required
from models.audit import get_recent_logs

bp = Blueprint("audit", __name__, url_prefix="/audit")

@bp.route("/")
@login_required
def list_logs():
    logs = get_recent_logs(limit=100)
    return render_template("audit/list.html", logs=logs)