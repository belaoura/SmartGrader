"""CSV student import service."""

import csv
import io
import logging

from app.models import db
from app.models.student import Student
from app.models.user import User

logger = logging.getLogger("smartgrader.services.import")


def import_students_csv(file):
    """Import students from a CSV file, creating Student + User records.

    Args:
        file: File-like object containing CSV data with columns: name, matricule, email.

    Returns:
        Dict with keys: created (int), skipped (int), errors (list of dicts).
    """
    content = file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8")

    reader = csv.DictReader(io.StringIO(content))

    created = 0
    skipped = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        name = (row.get("name") or "").strip()
        matricule = (row.get("matricule") or "").strip()
        email = (row.get("email") or "").strip()

        if not name or not matricule:
            errors.append({"row": row_num, "message": "Name and matricule are required"})
            continue

        existing = Student.query.filter_by(matricule=matricule).first()
        if existing:
            skipped += 1
            continue

        student = Student(name=name, matricule=matricule, email=email or None)
        db.session.add(student)
        db.session.flush()

        user = User(role="student", student_id=student.id)
        db.session.add(user)

        created += 1

    db.session.commit()

    logger.info("CSV import complete: created=%d, skipped=%d, errors=%d", created, skipped, len(errors))
    return {"created": created, "skipped": skipped, "errors": errors}
