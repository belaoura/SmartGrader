"""SQLAlchemy models for SmartGrader."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.exam import Exam, Question, Choice  # noqa: E402, F401
from app.models.student import Student, StudentAnswer  # noqa: E402, F401
from app.models.result import Result  # noqa: E402, F401
from app.models.ai_correction import AICorrection  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401
from app.models.group import StudentGroup, StudentGroupMember  # noqa: E402, F401
