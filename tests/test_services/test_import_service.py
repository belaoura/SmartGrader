"""Tests for CSV student import service."""

import io
from app.models.student import Student
from app.models.user import User
from app.services.import_service import import_students_csv


def test_import_valid_csv(db):
    csv_content = "name,matricule,email\nAli,001,ali@univ.dz\nFatima,002,fatima@univ.dz\n"
    file = io.BytesIO(csv_content.encode("utf-8"))

    result = import_students_csv(file)

    assert result["created"] == 2
    assert result["skipped"] == 0
    assert result["errors"] == []

    assert Student.query.count() == 2
    assert User.query.filter_by(role="student").count() == 2


def test_import_skip_duplicate_matricule(db):
    student = Student(name="Existing", matricule="001")
    db.session.add(student)
    db.session.commit()

    csv_content = "name,matricule,email\nAli,001,ali@univ.dz\nFatima,002,fatima@univ.dz\n"
    file = io.BytesIO(csv_content.encode("utf-8"))

    result = import_students_csv(file)

    assert result["created"] == 1
    assert result["skipped"] == 1


def test_import_missing_required_fields(db):
    csv_content = "name,matricule,email\n,001,ali@univ.dz\nFatima,,fatima@univ.dz\n"
    file = io.BytesIO(csv_content.encode("utf-8"))

    result = import_students_csv(file)

    assert result["created"] == 0
    assert len(result["errors"]) == 2


def test_import_empty_csv(db):
    csv_content = "name,matricule,email\n"
    file = io.BytesIO(csv_content.encode("utf-8"))

    result = import_students_csv(file)

    assert result["created"] == 0
    assert result["skipped"] == 0
