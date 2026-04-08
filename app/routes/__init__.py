"""Flask API route blueprints."""


def register_blueprints(app):
    """Register all route blueprints with the Flask app."""
    from app.routes.exams import exams_bp
    from app.routes.questions import questions_bp
    from app.routes.students import students_bp
    from app.routes.scanning import scanning_bp
    from app.routes.grading import grading_bp
    from app.routes.ai import ai_bp
    from app.routes.static_files import static_files_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.groups import groups_bp
    from app.routes.sessions import sessions_bp
    from app.routes.student_exam import student_exam_bp

    app.register_blueprint(exams_bp, url_prefix="/api")
    app.register_blueprint(questions_bp, url_prefix="/api")
    app.register_blueprint(students_bp, url_prefix="/api")
    app.register_blueprint(scanning_bp, url_prefix="/api")
    app.register_blueprint(grading_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(static_files_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api")
    app.register_blueprint(groups_bp, url_prefix="/api")
    app.register_blueprint(sessions_bp, url_prefix="/api")
    app.register_blueprint(student_exam_bp, url_prefix="/api")
