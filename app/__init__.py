"""SmartGrader Flask application."""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from app.config import config_by_name
from app.models import db
from app.logging_config import setup_logging
from app.errors import SmartGraderError

migrate = Migrate()
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
    CORS(app)

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

    # Health check
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "version": "0.2.0"})

    logger.info("SmartGrader app created [%s]", config_name)
    return app
