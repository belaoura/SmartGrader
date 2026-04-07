"""Seed database with sample data for development.

Usage: python -m scripts.seed_data
"""

import os
import sys
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from app.services.exam_service import create_exam, create_question_with_choices
from app.models.student import Student
from app.models.result import Result
from app.models.exam import Exam


EXAMS = [
    {
        "title": "Mathematics - Algebra",
        "subject": "Mathematics",
        "total_marks": 20,
        "questions": [
            {"text": "What is 2 + 2?", "marks": 5, "choices": [
                {"label": "A", "text": "3", "is_correct": False},
                {"label": "B", "text": "4", "is_correct": True},
                {"label": "C", "text": "5", "is_correct": False},
                {"label": "D", "text": "6", "is_correct": False},
            ]},
            {"text": "What is 5 x 3?", "marks": 5, "choices": [
                {"label": "A", "text": "8", "is_correct": False},
                {"label": "B", "text": "15", "is_correct": True},
                {"label": "C", "text": "20", "is_correct": False},
            ]},
            {"text": "Solve: x + 3 = 7", "marks": 5, "choices": [
                {"label": "A", "text": "x = 3", "is_correct": False},
                {"label": "B", "text": "x = 4", "is_correct": True},
                {"label": "C", "text": "x = 10", "is_correct": False},
                {"label": "D", "text": "x = 7", "is_correct": False},
            ]},
            {"text": "What is the square root of 16?", "marks": 5, "choices": [
                {"label": "A", "text": "2", "is_correct": False},
                {"label": "B", "text": "4", "is_correct": True},
                {"label": "C", "text": "8", "is_correct": False},
            ]},
        ],
    },
    {
        "title": "Biology - Cell Biology",
        "subject": "Biology",
        "total_marks": 20,
        "questions": [
            {"text": "What is the powerhouse of the cell?", "marks": 4, "choices": [
                {"label": "A", "text": "Nucleus", "is_correct": False},
                {"label": "B", "text": "Mitochondria", "is_correct": True},
                {"label": "C", "text": "Ribosome", "is_correct": False},
                {"label": "D", "text": "Golgi apparatus", "is_correct": False},
            ]},
            {"text": "Which organelle contains DNA?", "marks": 4, "choices": [
                {"label": "A", "text": "Nucleus", "is_correct": True},
                {"label": "B", "text": "Lysosome", "is_correct": False},
                {"label": "C", "text": "Vacuole", "is_correct": False},
            ]},
            {"text": "What is the function of ribosomes?", "marks": 4, "choices": [
                {"label": "A", "text": "Energy production", "is_correct": False},
                {"label": "B", "text": "Protein synthesis", "is_correct": True},
                {"label": "C", "text": "Cell division", "is_correct": False},
                {"label": "D", "text": "Waste removal", "is_correct": False},
            ]},
            {"text": "Cell membrane is made of:", "marks": 4, "choices": [
                {"label": "A", "text": "Carbohydrates", "is_correct": False},
                {"label": "B", "text": "Phospholipid bilayer", "is_correct": True},
                {"label": "C", "text": "Cellulose", "is_correct": False},
            ]},
            {"text": "Which process converts glucose to energy?", "marks": 4, "choices": [
                {"label": "A", "text": "Photosynthesis", "is_correct": False},
                {"label": "B", "text": "Cellular respiration", "is_correct": True},
                {"label": "C", "text": "Fermentation", "is_correct": False},
                {"label": "D", "text": "Osmosis", "is_correct": False},
            ]},
        ],
    },
    {
        "title": "Physics - Mechanics",
        "subject": "Physics",
        "total_marks": 25,
        "questions": [
            {"text": "Newton's first law describes:", "marks": 5, "choices": [
                {"label": "A", "text": "Inertia", "is_correct": True},
                {"label": "B", "text": "Acceleration", "is_correct": False},
                {"label": "C", "text": "Action-reaction", "is_correct": False},
            ]},
            {"text": "F = ma is Newton's ___ law", "marks": 5, "choices": [
                {"label": "A", "text": "First", "is_correct": False},
                {"label": "B", "text": "Second", "is_correct": True},
                {"label": "C", "text": "Third", "is_correct": False},
                {"label": "D", "text": "Fourth", "is_correct": False},
            ]},
            {"text": "Unit of force is:", "marks": 5, "choices": [
                {"label": "A", "text": "Joule", "is_correct": False},
                {"label": "B", "text": "Newton", "is_correct": True},
                {"label": "C", "text": "Watt", "is_correct": False},
            ]},
            {"text": "Acceleration due to gravity is approximately:", "marks": 5, "choices": [
                {"label": "A", "text": "9.8 m/s\u00b2", "is_correct": True},
                {"label": "B", "text": "10.2 m/s\u00b2", "is_correct": False},
                {"label": "C", "text": "8.5 m/s\u00b2", "is_correct": False},
                {"label": "D", "text": "11.0 m/s\u00b2", "is_correct": False},
            ]},
            {"text": "Work is defined as:", "marks": 5, "choices": [
                {"label": "A", "text": "Force \u00d7 Distance", "is_correct": True},
                {"label": "B", "text": "Mass \u00d7 Velocity", "is_correct": False},
                {"label": "C", "text": "Power \u00d7 Time", "is_correct": False},
            ]},
        ],
    },
    {
        "title": "Chemistry - Organic",
        "subject": "Chemistry",
        "total_marks": 20,
        "questions": [
            {"text": "Carbon can form how many bonds?", "marks": 5, "choices": [
                {"label": "A", "text": "2", "is_correct": False},
                {"label": "B", "text": "4", "is_correct": True},
                {"label": "C", "text": "6", "is_correct": False},
            ]},
            {"text": "Methane's formula is:", "marks": 5, "choices": [
                {"label": "A", "text": "CH4", "is_correct": True},
                {"label": "B", "text": "C2H6", "is_correct": False},
                {"label": "C", "text": "CO2", "is_correct": False},
                {"label": "D", "text": "C2H4", "is_correct": False},
            ]},
            {"text": "An alcohol contains which functional group?", "marks": 5, "choices": [
                {"label": "A", "text": "-OH", "is_correct": True},
                {"label": "B", "text": "-COOH", "is_correct": False},
                {"label": "C", "text": "-NH2", "is_correct": False},
            ]},
            {"text": "Benzene has how many carbon atoms?", "marks": 5, "choices": [
                {"label": "A", "text": "4", "is_correct": False},
                {"label": "B", "text": "6", "is_correct": True},
                {"label": "C", "text": "8", "is_correct": False},
                {"label": "D", "text": "12", "is_correct": False},
            ]},
        ],
    },
    {
        "title": "Computer Science - Algorithms",
        "subject": "Computer Science",
        "total_marks": 25,
        "questions": [
            {"text": "Time complexity of binary search:", "marks": 5, "choices": [
                {"label": "A", "text": "O(n)", "is_correct": False},
                {"label": "B", "text": "O(log n)", "is_correct": True},
                {"label": "C", "text": "O(n\u00b2)", "is_correct": False},
                {"label": "D", "text": "O(1)", "is_correct": False},
            ]},
            {"text": "Which data structure uses FIFO?", "marks": 5, "choices": [
                {"label": "A", "text": "Stack", "is_correct": False},
                {"label": "B", "text": "Queue", "is_correct": True},
                {"label": "C", "text": "Array", "is_correct": False},
            ]},
            {"text": "A stack uses which principle?", "marks": 5, "choices": [
                {"label": "A", "text": "FIFO", "is_correct": False},
                {"label": "B", "text": "LIFO", "is_correct": True},
                {"label": "C", "text": "Random", "is_correct": False},
                {"label": "D", "text": "Priority", "is_correct": False},
            ]},
            {"text": "Worst case of bubble sort:", "marks": 5, "choices": [
                {"label": "A", "text": "O(n)", "is_correct": False},
                {"label": "B", "text": "O(n log n)", "is_correct": False},
                {"label": "C", "text": "O(n\u00b2)", "is_correct": True},
            ]},
            {"text": "Which is a divide-and-conquer algorithm?", "marks": 5, "choices": [
                {"label": "A", "text": "Bubble sort", "is_correct": False},
                {"label": "B", "text": "Merge sort", "is_correct": True},
                {"label": "C", "text": "Insertion sort", "is_correct": False},
                {"label": "D", "text": "Selection sort", "is_correct": False},
            ]},
        ],
    },
]

STUDENTS = [
    {"name": "Ahmed Benali", "matricule": "2026001", "email": "ahmed@univ.dz"},
    {"name": "Fatima Zahra", "matricule": "2026002", "email": "fatima@univ.dz"},
    {"name": "Mohamed Amine", "matricule": "2026003", "email": "amine@univ.dz"},
    {"name": "Amina Boudiaf", "matricule": "2026004", "email": "amina@univ.dz"},
    {"name": "Youcef Khelifi", "matricule": "2026005", "email": "youcef@univ.dz"},
    {"name": "Sara Mebarki", "matricule": "2026006", "email": "sara@univ.dz"},
    {"name": "Rachid Hamidi", "matricule": "2026007", "email": "rachid@univ.dz"},
    {"name": "Nour El Houda", "matricule": "2026008", "email": "nour@univ.dz"},
    {"name": "Karim Zidane", "matricule": "2026009", "email": "karim@univ.dz"},
    {"name": "Lina Benmoussa", "matricule": "2026010", "email": "lina@univ.dz"},
]


def seed():
    """Insert sample data if not already present."""
    app = create_app("development")

    with app.app_context():
        db.create_all()

        # Seed exams and questions
        created_exams = []
        for exam_data in EXAMS:
            existing = Exam.query.filter_by(title=exam_data["title"]).first()
            if existing:
                print(f"  Exam '{exam_data['title']}' already exists, skipping")
                created_exams.append(existing)
                continue

            exam = create_exam(
                title=exam_data["title"],
                subject=exam_data["subject"],
                date="2026-04-06",
                total_marks=exam_data["total_marks"],
            )
            for q in exam_data["questions"]:
                create_question_with_choices(
                    exam_id=exam.id,
                    question_text=q["text"],
                    marks=q["marks"],
                    choices=q["choices"],
                )
            created_exams.append(exam)
            print(f"  Created exam: {exam_data['title']} ({len(exam_data['questions'])} questions)")

        # Seed students
        created_students = []
        for s in STUDENTS:
            existing = Student.query.filter_by(matricule=s["matricule"]).first()
            if existing:
                created_students.append(existing)
                continue
            student = Student(name=s["name"], matricule=s["matricule"], email=s["email"])
            db.session.add(student)
            created_students.append(student)
        db.session.commit()
        print(f"  Students: {len(created_students)} total")

        # Seed results
        random.seed(42)
        results_count = 0
        for exam in created_exams:
            existing_results = Result.query.filter_by(exam_id=exam.id).count()
            if existing_results > 0:
                print(f"  Results for '{exam.title}' already exist, skipping")
                continue

            num_students = random.randint(6, min(8, len(created_students)))
            selected = random.sample(created_students, num_students)

            for student in selected:
                score_pct = random.uniform(0.45, 1.0)
                score = round(exam.total_marks * score_pct, 1)
                percentage = round(score_pct * 100, 1)
                result = Result(
                    student_id=student.id,
                    exam_id=exam.id,
                    score=score,
                    percentage=percentage,
                    graded_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                db.session.add(result)
                results_count += 1

        db.session.commit()
        print(f"  Results: {results_count} new results seeded")
        print(f"\nDone: {len(EXAMS)} exams, {len(STUDENTS)} students, {results_count} results")


if __name__ == "__main__":
    seed()
