"""Seed database with sample data for development.

Usage: python -m scripts.seed_data
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from app.services.exam_service import create_exam, create_question_with_choices
from app.models.student import Student


def seed():
    """Insert sample data."""
    app = create_app("development")

    with app.app_context():
        db.create_all()

        exam = create_exam(
            title="Mathematics - Algebra",
            subject="Mathematics",
            date="2026-04-06",
            total_marks=20,
        )

        create_question_with_choices(
            exam_id=exam.id,
            question_text="What is 2 + 2?",
            marks=5,
            choices=[
                {"label": "A", "text": "3", "is_correct": False},
                {"label": "B", "text": "4", "is_correct": True},
                {"label": "C", "text": "5", "is_correct": False},
                {"label": "D", "text": "6", "is_correct": False},
            ],
        )

        create_question_with_choices(
            exam_id=exam.id,
            question_text="What is 5 x 3?",
            marks=5,
            choices=[
                {"label": "A", "text": "8", "is_correct": False},
                {"label": "B", "text": "15", "is_correct": True},
                {"label": "C", "text": "20", "is_correct": False},
            ],
        )

        create_question_with_choices(
            exam_id=exam.id,
            question_text="Solve: x + 3 = 7",
            marks=5,
            choices=[
                {"label": "A", "text": "x = 3", "is_correct": False},
                {"label": "B", "text": "x = 4", "is_correct": True},
                {"label": "C", "text": "x = 10", "is_correct": False},
                {"label": "D", "text": "x = 7", "is_correct": False},
            ],
        )

        create_question_with_choices(
            exam_id=exam.id,
            question_text="What is the square root of 16?",
            marks=5,
            choices=[
                {"label": "A", "text": "2", "is_correct": False},
                {"label": "B", "text": "4", "is_correct": True},
                {"label": "C", "text": "8", "is_correct": False},
            ],
        )

        s1 = Student(name="Ahmed Benali", matricule="2026001", email="ahmed@univ.dz")
        s2 = Student(name="Fatima Zahra", matricule="2026002", email="fatima@univ.dz")
        s3 = Student(name="Mohamed Amine", matricule="2026003", email="amine@univ.dz")
        db.session.add_all([s1, s2, s3])
        db.session.commit()

        print(f"Seeded: 1 exam, 4 questions, 3 students")


if __name__ == "__main__":
    seed()
