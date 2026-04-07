"""Centralized configuration for SmartGrader."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "smart_grader.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Sheet generation (A4 dimensions in mm)
    PAGE_HEIGHT_MM = 297
    PAGE_WIDTH_MM = 210
    MARGIN_MM = {"top": 8, "bottom": 8, "left": 12, "right": 12}
    HEADER_HEIGHT_MM = 28
    MINIMAL_HEADER_HEIGHT_MM = 10
    STUDENT_SECTION_HEIGHT_MM = 36
    INSTRUCTION_HEIGHT_MM = 8
    PAGE_NUMBER_HEIGHT_MM = 6
    GRID_GAP_MM = 2
    LINE_HEIGHT_MM = 4.3
    OPTION_SPACING_MM = 1.2
    QUESTION_BOTTOM_MM = 3.5
    MIN_QUESTION_HEIGHT_MM = 10
    CHARS_PER_LINE = 62
    HEIGHT_SAFETY_BUFFER_MM = 4

    # Scanner thresholds
    FILL_THRESHOLD = 50
    CIRCLE_AREA_MIN = 60
    CIRCLE_AREA_MAX = 600
    CIRCULARITY_MIN = 0.65
    ASPECT_RATIO_MIN = 0.6
    ASPECT_RATIO_MAX = 1.5
    RADIUS_MIN = 6
    RADIUS_MAX = 25
    DUPLICATE_DISTANCE = 10
    OUTLIER_MAX_DEVIATION = 50

    # Column detection (as fraction of image width)
    LEFT_COL_MIN = 0.08
    LEFT_COL_MAX = 0.25
    RIGHT_COL_MIN = 0.45
    RIGHT_COL_MAX = 0.75

    # PDF generation
    PDF_DPI = 300
    PDFKIT_OPTIONS = {
        "page-size": "A4",
        "margin-top": "0mm",
        "margin-right": "0mm",
        "margin-bottom": "0mm",
        "margin-left": "0mm",
        "encoding": "UTF-8",
        "enable-local-file-access": "",
    }

    # Smart grading features
    SMART_GRADING_ENABLED = True
    GENERATE_ANSWER_KEY = True
    INCLUDE_OMR_MARKERS = True

    # AI model (Sub-Project 3 -- placeholders)
    VISION_MODEL = "Qwen/Qwen2.5-VL-3B-Instruct"
    MODEL_DEVICE = "cuda"
    MAX_TOKENS = 512
    CONFIDENCE_THRESHOLD = 0.7

    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "tiff", "bmp"}

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = os.path.join(BASE_DIR, "logs", "smartgrader.log")

    # Authentication
    JWT_ACCESS_TOKEN_EXPIRES = 900        # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 604800    # 7 days
    BCRYPT_LOG_ROUNDS = 12
    RATELIMIT_LOGIN = "5 per minute"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOG_LEVEL = "WARNING"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = "WARNING"


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
