"""Tests for auth service."""

import pytest
from app.models.user import User
from app.models.student import Student
from app.models import db as _db
from app.services.auth_service import (
    create_teacher,
    login_teacher,
    login_student,
    logout_user,
)
from app.errors import AuthenticationError, NotFoundError


def test_create_teacher(db):
    user = create_teacher(
        email="prof@univ.dz",
        password="securepass",
        name="Prof Ahmed",
        is_admin=False,
    )
    assert user.id is not None
    assert user.email == "prof@univ.dz"
    assert user.role == "teacher"
    assert user.password_hash is not None
    assert user.password_hash != "securepass"


def test_create_admin_teacher(db):
    user = create_teacher(
        email="admin@univ.dz",
        password="adminpass",
        name="Admin",
        is_admin=True,
    )
    assert user.is_admin is True


def test_create_teacher_duplicate_email(db):
    create_teacher(email="dup@univ.dz", password="pass1234", name="A")
    with pytest.raises(AuthenticationError, match="already exists"):
        create_teacher(email="dup@univ.dz", password="pass1234", name="B")


def test_login_teacher_success(app, db):
    create_teacher(email="login@univ.dz", password="mypassword", name="T")

    with app.test_request_context():
        user = login_teacher("login@univ.dz", "mypassword")
        assert user.email == "login@univ.dz"


def test_login_teacher_wrong_password(app, db):
    create_teacher(email="wrong@univ.dz", password="correct1", name="T")

    with app.test_request_context():
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            login_teacher("wrong@univ.dz", "incorrect")


def test_login_teacher_unknown_email(app, db):
    with app.test_request_context():
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            login_teacher("nobody@univ.dz", "pass1234")


def test_login_teacher_inactive(app, db):
    user = create_teacher(email="inactive@univ.dz", password="pass1234", name="T")
    user.is_active = False
    db.session.commit()

    with app.test_request_context():
        with pytest.raises(AuthenticationError, match="Account is disabled"):
            login_teacher("inactive@univ.dz", "pass1234")


def test_login_teacher_bumps_token_version(app, db):
    create_teacher(email="bump@univ.dz", password="pass1234", name="T")

    with app.test_request_context():
        user = login_teacher("bump@univ.dz", "pass1234")
        assert user.token_version == 1
        user = login_teacher("bump@univ.dz", "pass1234")
        assert user.token_version == 2


def test_login_student_success(app, db):
    student = Student(name="Ali", matricule="2026001", email="ali@univ.dz")
    db.session.add(student)
    db.session.commit()

    user = User(role="student", student_id=student.id)
    db.session.add(user)
    db.session.commit()

    with app.test_request_context():
        result = login_student("2026001")
        assert result.role == "student"
        assert result.student_id == student.id


def test_login_student_unknown_matricule(app, db):
    with app.test_request_context():
        with pytest.raises(NotFoundError):
            login_student("UNKNOWN")


def test_login_student_no_user_account(app, db):
    student = Student(name="NoUser", matricule="999")
    db.session.add(student)
    db.session.commit()

    with app.test_request_context():
        with pytest.raises(AuthenticationError, match="No account"):
            login_student("999")


def test_logout_bumps_token_version(db):
    user = create_teacher(email="out@univ.dz", password="pass1234", name="T")
    old_ver = user.token_version
    logout_user(user.id)
    assert user.token_version == old_ver + 1
