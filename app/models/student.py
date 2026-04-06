"""Student and StudentAnswer models."""

from app.models import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    matricule = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(200))

    answers = db.relationship(
        "StudentAnswer", backref="student", cascade="all, delete-orphan", lazy="dynamic"
    )
    results = db.relationship(
        "Result", backref="student", cascade="all, delete-orphan", lazy="dynamic"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "matricule": self.matricule,
            "email": self.email,
        }


class StudentAnswer(db.Model):
    __tablename__ = "student_answers"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    selected_choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"))

    selected_choice = db.relationship("Choice", foreign_keys=[selected_choice_id])

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "question_id": self.question_id,
            "selected_choice_id": self.selected_choice_id,
        }
