"""
routes/requirements.py — إدارة المتطلبات (v2.0)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.requirement import (
    get_requirement, create_requirement, update_requirement, delete_requirement,
)
from models.audit import log_action
from models.db import execute_one

bp = Blueprint("requirements", __name__, url_prefix="/requirements")


@bp.route("/new/<int:project_id>", methods=["GET", "POST"])
@login_required
def new_requirement(project_id):
    # جلب المشروع مباشرة من قاعدة البيانات
    project = execute_one("SELECT * FROM projects WHERE id = %s", (project_id,))
    if not project:
        flash("المشروع غير موجود", "error")
        return redirect(url_for("projects.list_projects"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "open")

        if not title:
            flash("عنوان المتطلب مطلوب", "error")
            return render_template("requirements/form.html", project=project, requirement=None)

        req_id = create_requirement(project_id, title, description, status)
        log_action("CREATE_REQUIREMENT", "requirement", req_id, title)

        flash("تمت إضافة المتطلب", "success")
        return redirect(url_for("projects.detail_project", project_id=project_id))

    return render_template("requirements/form.html", project=project, requirement=None)


@bp.route("/<int:req_id>/edit", methods=["GET", "POST"])
@login_required
def edit_requirement(req_id):
    requirement = get_requirement(req_id)
    if not requirement:
        flash("المتطلب غير موجود", "error")
        return redirect(url_for("projects.list_projects"))

    # جلب المشروع مباشرة
    project = execute_one("SELECT * FROM projects WHERE id = %s", (requirement["project_id"],))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "open")

        if not title:
            flash("عنوان المتطلب مطلوب", "error")
            return render_template("requirements/form.html", project=project, requirement=requirement)

        update_requirement(req_id, title, description, status)
        log_action("UPDATE_REQUIREMENT", "requirement", req_id, title)

        flash("تم تحديث المتطلب", "success")
        return redirect(url_for("projects.detail_project", project_id=project["id"]))

    return render_template("requirements/form.html", project=project, requirement=requirement)


@bp.route("/<int:req_id>/delete", methods=["POST"])
@login_required
def delete_requirement_route(req_id):
    requirement = get_requirement(req_id)
    if not requirement:
        flash("المتطلب غير موجود", "error")
        return redirect(url_for("projects.list_projects"))

    project_id = requirement["project_id"]
    delete_requirement(req_id)
    log_action("DELETE_REQUIREMENT", "requirement", req_id, requirement["title"])

    flash("تم حذف المتطلب", "success")
    return redirect(url_for("projects.detail_project", project_id=project_id))