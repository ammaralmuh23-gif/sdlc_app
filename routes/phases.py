"""
routes/phases.py — إدارة المراحل
"""
from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required
from models.phase import get_phase, update_phase_status
from models.audit import log_action

bp = Blueprint("phases", __name__, url_prefix="/phases")

VALID_STATUSES = ("pending", "in_progress", "completed")

@bp.route("/<int:phase_id>/status", methods=["POST"])
@login_required
def change_status(phase_id):
    phase = get_phase(phase_id)
    if not phase:
        flash("المرحلة غير موجودة", "error")
        return redirect(url_for("projects.list_projects"))

    new_status = request.form.get("status", "").strip()

    if new_status not in VALID_STATUSES:
        flash("حالة غير صالحة", "error")
        return redirect(url_for("projects.detail_project", project_id=phase["project_id"]))

    if new_status == phase["status"]:
        return redirect(url_for("projects.detail_project", project_id=phase["project_id"]))

    update_phase_status(phase_id, new_status)
    log_action("UPDATE_PHASE", "phase", phase_id, f"{phase['name']}: {phase['status']} → {new_status}")

    flash("تم تحديث حالة المرحلة", "success")
    return redirect(url_for("projects.detail_project", project_id=phase["project_id"]))