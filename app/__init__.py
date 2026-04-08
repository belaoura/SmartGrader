"""SmartGrader Flask application."""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import config_by_name
from app.models import db
from app.logging_config import setup_logging
from app.errors import SmartGraderError

migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger("smartgrader")


def create_app(config_name=None):
    """Application factory.

    Args:
        config_name: One of 'development', 'testing', 'production'.
                     Defaults to FLASK_ENV or 'development'.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    origins = app.config.get("ALLOWED_ORIGINS", "*")
    if origins != "*":
        origins = [o.strip() for o in origins.split(",")]
    CORS(app, origins=origins)
    limiter.init_app(app)

    # Setup logging
    setup_logging(
        log_level=app.config.get("LOG_LEVEL", "INFO"),
        log_file=app.config.get("LOG_FILE"),
    )

    # Register error handlers
    @app.errorhandler(SmartGraderError)
    def handle_smartgrader_error(error):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def handle_500(error):
        logger.exception("Internal server error")
        return jsonify({"error": "Internal server error"}), 500

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    # Serve frontend static files (LAN/Docker mode)
    if app.config.get("SERVE_STATIC"):
        import os as _os
        dist_dir = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), "frontend", "dist")
        if _os.path.isdir(dist_dir):
            from flask import send_from_directory

            @app.route("/assets/<path:filename>")
            def serve_assets(filename):
                return send_from_directory(_os.path.join(dist_dir, "assets"), filename)

            @app.route("/", defaults={"path": ""})
            @app.route("/<path:path>")
            def serve_frontend(path):
                if path.startswith("api/"):
                    return jsonify({"error": "Not found"}), 404
                return send_from_directory(dist_dir, "index.html")

    # Health check
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "version": "0.2.0"})

    logger.info("SmartGrader app created [%s]", config_name)
    return app
