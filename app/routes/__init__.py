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

    app.register_blueprint(exams_bp, url_prefix="/api")
    app.register_blueprint(questions_bp, url_prefix="/api")
    app.register_blueprint(students_bp, url_prefix="/api")
    app.register_blueprint(scanning_bp, url_prefix="/api")
    app.register_blueprint(grading_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(static_files_bp, url_prefix="/api")
