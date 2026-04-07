"""Authentication service — login, logout, token management."""

import logging
import re

import bcrypt

from app.models import db
from app.models.user import User
from app.models.student import Student
from app.errors import AuthenticationError, NotFoundError

logger = logging.getLogger("smartgrader.services.auth")


def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, password_hash):
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_teacher(email, password, name, is_admin=False):
    """Create a new teacher user account.

    Args:
        email: Teacher email address.
        password: Plaintext password (min 8 chars).
        name: Display name.
        is_admin: Whether this teacher has admin privileges.

    Returns:
        The created User object.

    Raises:
        AuthenticationError: If email already exists or validation fails.
    """
    if not email or not password or not name:
        raise AuthenticationError("Email, password, and name are required")
    if len(password) < 8:
        raise AuthenticationError("Password must be at least 8 characters")

    existing = User.query.filter_by(email=email).first()
    if existing:
        raise AuthenticationError(f"User with email {email} already exists")

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="teacher",
        is_admin=is_admin,
    )
    db.session.add(user)
    db.session.commit()

    logger.info("Created teacher account: %s (admin=%s)", email, is_admin)
    return user


def login_teacher(email, password):
    """Authenticate a teacher by email and password.

    Args:
        email: Teacher email address.
        password: Plaintext password.

    Returns:
        The authenticated User object (token_version bumped).

    Raises:
        AuthenticationError: If credentials are invalid or account is disabled.
    """
    user = User.query.filter_by(email=email, role="teacher").first()
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    user.token_version += 1
    db.session.commit()

    logger.info("Teacher logged in: %s", email)
    return user


def login_student(matricule):
    """Authenticate a student by matricule (from barcode scan).

    Args:
        matricule: Student matricule number.

    Returns:
        The authenticated User object (token_version bumped).

    Raises:
        NotFoundError: If no student with this matricule.
        AuthenticationError: If student has no user account or is disabled.
    """
    sanitized = re.sub(r"[^a-zA-Z0-9]", "", matricule)
    student = Student.query.filter_by(matricule=sanitized).first()
    if not student:
        raise NotFoundError("Student", sanitized)

    user = User.query.filter_by(student_id=student.id, role="student").first()
    if not user:
        raise AuthenticationError("No account linked to this student")

    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    user.token_version += 1
    db.session.commit()

    logger.info("Student logged in: %s", sanitized)
    return user


def logout_user(user_id):
    """Invalidate all tokens for a user by bumping token_version.

    Args:
        user_id: The user ID to log out.
    """
    user = User.query.get(user_id)
    if user:
        user.token_version += 1
        db.session.commit()
        logger.info("User logged out: %s", user_id)
