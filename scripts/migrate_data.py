"""Migrate data from legacy SQLite database to new SQLAlchemy models.

Usage: python -m scripts.migrate_data [path_to_old_db]
"""

import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from app.models.exam import Exam, Question, Choice
from app.models.student import Student, StudentAnswer
from app.models.result import Result


def migrate(old_db_path):
    """Migrate data from old database to new."""
    if not os.path.exists(old_db_path):
        print(f"Old database not found: {old_db_path}")
        return

    app = create_app("development")
    old_conn = sqlite3.connect(old_db_path)
    old_cur = old_conn.cursor()

    with app.app_context():
        db.create_all()

        old_cur.execute("SELECT id, title, subject, date, total_marks FROM exams")
        for row in old_cur.fetchall():
            exam = Exam(id=row[0], title=row[1], subject=row[2], date=row[3], total_marks=row[4])
            db.session.add(exam)
        db.session.commit()
        print(f"Migrated {Exam.query.count()} exams")

        old_cur.execute("SELECT id, exam_id, question_text, question_choices_number, marks FROM questions")
        for row in old_cur.fetchall():
            q = Question(id=row[0], exam_id=row[1], question_text=row[2], question_choices_number=row[3], marks=row[4])
            db.session.add(q)
        db.session.commit()
        print(f"Migrated {Question.query.count()} questions")

        old_cur.execute("SELECT id, question_id, choice_label, choice_text, is_correct FROM choices")
        for row in old_cur.fetchall():
            c = Choice(id=row[0], question_id=row[1], choice_label=row[2], choice_text=row[3], is_correct=row[4])
            db.session.add(c)
        db.session.commit()
        print(f"Migrated {Choice.query.count()} choices")

        old_cur.execute("SELECT id, name, matricule, email FROM students")
        for row in old_cur.fetchall():
            s = Student(id=row[0], name=row[1], matricule=row[2], email=row[3])
            db.session.add(s)
        db.session.commit()
        print(f"Migrated {Student.query.count()} students")

        old_cur.execute("SELECT id, student_id, exam_id, score, percentage, graded_at FROM results")
        for row in old_cur.fetchall():
            r = Result(id=row[0], student_id=row[1], exam_id=row[2], score=row[3], percentage=row[4], graded_at=row[5])
            db.session.add(r)
        db.session.commit()
        print(f"Migrated {Result.query.count()} results")

    old_conn.close()
    print("Migration complete!")


if __name__ == "__main__":
    old_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "smart_grader.db"
    )
    migrate(old_path)
