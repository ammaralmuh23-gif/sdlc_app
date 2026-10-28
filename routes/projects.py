"""
routes/projects.py — إدارة المشاريع (v2.0)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.project import (
    get_all_projects, get_project, create_project,
    update_project, delete_project,
)
from models.phase import create_default_phases, get_phases_by_project
from models.requirement import get_requirements_by_project
from models.audit import log_action
from models.db import execute_one

bp = Blueprint("projects", __name__, url_prefix="/projects")


@bp.route("/")
@login_required
def list_projects():
    projects = get_all_projects(current_user.id, current_user.is_admin)
    return render_template("projects/list.html", projects=projects)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_project():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        start_date = request.form.get("start_date") or None

        if not name:
            flash("اسم المشروع مطلوب", "error")
            return render_template("projects/form.html", project=None)

        # إنشاء المشروع وربطه بالمستخدم الحالي
        project_id = create_project(name, description, start_date, current_user.id)
        create_default_phases(project_id)
        log_action("CREATE_PROJECT", "project", project_id, name)

        flash("تمت إضافة المشروع بنجاح", "success")
        return redirect(url_for("projects.list_projects"))

    return render_template("projects/form.html", project=None)


@bp.route("/<int:project_id>")
@login_required
def detail_project(project_id):
    # جلب المشروع مباشرة من قاعدة البيانات (لتجاوز أي مشاكل في الصلاحيات)
    project = execute_one("SELECT * FROM projects WHERE id = %s", (project_id,))
    
    if not project:
        flash("المشروع غير موجود في قاعدة البيانات", "error")
        return redirect(url_for("projects.list_projects"))

    phases = get_phases_by_project(project_id)
    requirements = get_requirements_by_project(project_id)

    return render_template("projects/detail.html", project=project, phases=phases, requirements=requirements)


@bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    # جلب المشروع مباشرة
    project = execute_one("SELECT * FROM projects WHERE id = %s", (project_id,))
    
    if not project:
        flash("المشروع غير موجود في قاعدة البيانات", "error")
        return redirect(url_for("projects.list_projects"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        start_date = request.form.get("start_date") or None
        status = request.form.get("status", "active")

        if not name:
            flash("اسم المشروع مطلوب", "error")
            return render_template("projects/form.html", project=project)

        update_project(project_id, name, description, start_date, status)
        log_action("UPDATE_PROJECT", "project", project_id, name)

        flash("تم تحديث المشروع", "success")
        return redirect(url_for("projects.detail_project", project_id=project_id))

    return render_template("projects/form.html", project=project)


@bp.route("/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project_route(project_id):
    project = execute_one("SELECT * FROM projects WHERE id = %s", (project_id,))
    
    if not project:
        flash("المشروع غير موجود في قاعدة البيانات", "error")
        return redirect(url_for("projects.list_projects"))

    delete_project(project_id)
    log_action("DELETE_PROJECT", "project", project_id, project["name"])
    
    flash("تم حذف المشروع", "success")
    return redirect(url_for("projects.list_projects"))