"""
routes/reports.py — التقارير وتصدير CSV (v2.0)
"""
import csv
import io
from flask import Blueprint, render_template, Response, flash, redirect, url_for
from flask_login import login_required
from models.project import get_project
from models.phase import get_phases_by_project
from models.requirement import get_requirements_by_project
from models.audit import log_action
from models.db import execute_one

bp = Blueprint("reports", __name__, url_prefix="/projects")


# دالة مساعدة لترجمة الحالات
def translate_status(status):
    translations = {
        "active": "نشط",
        "archived": "مؤرشف",
        "pending": "معلقة",
        "in_progress": "قيد العمل",
        "completed": "مكتملة",
        "open": "مفتوح",
        "done": "منجز"
    }
    return translations.get(status, status)


@bp.route("/<int:project_id>/report")
@login_required
def project_report(project_id):
    # جلب المشروع مباشرة لتجاوز مشاكل الصلاحيات
    project = execute_one("SELECT * FROM projects WHERE id = %s", (project_id,))
    
    if not project:
        flash("المشروع غير موجود", "error")
        return redirect(url_for("projects.list_projects"))

    phases = get_phases_by_project(project_id)
    requirements = get_requirements_by_project(project_id)

    return render_template(
        "reports/project_report.html",
        project=project,
        phases=phases,
        requirements=requirements,
        translate_status=translate_status # تمرير الدالة للقالب
    )


@bp.route("/<int:project_id>/export.csv")
@login_required
def export_csv(project_id):
    # جلب المشروع مباشرة
    project = execute_one("SELECT * FROM projects WHERE id = %s", (project_id,))
    
    if not project:
        flash("المشروع غير موجود", "error")
        return redirect(url_for("projects.list_projects"))

    phases = get_phases_by_project(project_id)
    requirements = get_requirements_by_project(project_id)

    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.writer(output)

    # قسم 1: بيانات المشروع
    writer.writerow(["=== بيانات المشروع ==="])
    writer.writerow(["الرقم", project["id"]])
    writer.writerow(["الاسم", project["name"]])
    writer.writerow(["الوصف", project["description"] or ""])
    writer.writerow(["تاريخ البدء", project["start_date"] or ""])
    
    # ترجمة حالة المشروع
    writer.writerow(["الحالة", translate_status(project["status"])])
    writer.writerow([])

    # قسم 2: المراحل
    writer.writerow(["=== المراحل ==="])
    writer.writerow(["#", "الاسم", "الحالة", "الترتيب"])
    for p in phases:
        # ترجمة حالة المرحلة
        writer.writerow([p["id"], p["name"], translate_status(p["status"]), p["order_index"]])
    writer.writerow([])

    # قسم 3: المتطلبات
    writer.writerow(["=== المتطلبات ==="])
    writer.writerow(["#", "العنوان", "الوصف", "الحالة"])
    for r in requirements:
        # ترجمة حالة المتطلب
        writer.writerow([r["id"], r["title"], r["description"] or "", translate_status(r["status"])])

    log_action("EXPORT_CSV", "project", project_id, project["name"])

    csv_data = output.getvalue()
    output.close()

    filename = f"project_{project_id}.csv"
    return Response(
        csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
