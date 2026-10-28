"""
app.py — نقطة تشغيل SDLC Manager v2.0
مع Flask-Login لتسجيل الدخول
"""
from flask import Flask
from flask_login import LoginManager, current_user
from config import Config
from models.user import get_user


login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ===== Flask-Login setup =====
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "يجب تسجيل الدخول أولاً."
    login_manager.login_message_category = "error"

    # ===== حقن current_user في كل القوالب =====
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    # ===== Blueprints =====
    from routes.auth import bp as auth_bp
    from routes.dashboard import bp as dashboard_bp
    from routes.projects import bp as projects_bp
    from routes.phases import bp as phases_bp
    from routes.requirements import bp as requirements_bp
    from routes.reports import bp as reports_bp
    from routes.audit import bp as audit_bp
    from routes.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(phases_bp)
    app.register_blueprint(requirements_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(admin_bp)

    return app


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login يستخدمها لتحميل المستخدم من الجلسة."""
    return get_user(int(user_id))


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)