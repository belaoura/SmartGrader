"""Tests for User model."""

import pytest
import sqlalchemy
from app.models.user import User
from app.models.student import Student
from app.models import db as _db


def test_create_teacher_user(db):
    user = User(
        name="Prof Ahmed",
        email="ahmed@univ.dz",
        password_hash="fakehash",
        role="teacher",
    )
    db.session.add(user)
    db.session.commit()

    assert user.id is not None
    assert user.role == "teacher"
    assert user.is_admin is False
    assert user.is_active is True
    assert user.token_version == 0
    assert user.student_id is None


def test_create_student_user(db):
    student = Student(name="Fatima", matricule="2026001", email="fatima@univ.dz")
    db.session.add(student)
    db.session.commit()

    user = User(role="student", student_id=student.id)
    db.session.add(user)
    db.session.commit()

    assert user.id is not None
    assert user.role == "student"
    assert user.student_id == student.id
    assert user.student.name == "Fatima"
    assert user.email is None
    assert user.password_hash is None


def test_teacher_unique_email(db):
    u1 = User(name="A", email="same@univ.dz", password_hash="h", role="teacher")
    u2 = User(name="B", email="same@univ.dz", password_hash="h", role="teacher")
    db.session.add(u1)
    db.session.commit()

    db.session.add(u2)
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_student_users_allow_null_email(db):
    s1 = Student(name="A", matricule="001")
    s2 = Student(name="B", matricule="002")
    db.session.add_all([s1, s2])
    db.session.commit()

    u1 = User(role="student", student_id=s1.id)
    u2 = User(role="student", student_id=s2.id)
    db.session.add_all([u1, u2])
    db.session.commit()

    assert u1.email is None
    assert u2.email is None


def test_user_to_dict_teacher(db):
    user = User(name="Prof", email="prof@univ.dz", password_hash="h", role="teacher", is_admin=True)
    db.session.add(user)
    db.session.commit()

    d = user.to_dict()
    assert d["name"] == "Prof"
    assert d["email"] == "prof@univ.dz"
    assert d["role"] == "teacher"
    assert d["is_admin"] is True
    assert "password_hash" not in d


def test_user_to_dict_student(db):
    student = Student(name="Ali", matricule="003")
    db.session.add(student)
    db.session.commit()

    user = User(role="student", student_id=student.id)
    db.session.add(user)
    db.session.commit()

    d = user.to_dict()
    assert d["name"] == "Ali"
    assert d["role"] == "student"
    assert d["student_id"] == student.id


def test_token_version_bump(db):
    user = User(name="T", email="t@t.dz", password_hash="h", role="teacher")
    db.session.add(user)
    db.session.commit()

    assert user.token_version == 0
    user.token_version += 1
    db.session.commit()
    assert user.token_version == 1
