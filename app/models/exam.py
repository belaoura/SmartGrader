"""Exam, Question, and Choice models."""

from app.models import db


class Exam(db.Model):
    __tablename__ = "exams"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100))
    date = db.Column(db.String(20))
    total_marks = db.Column(db.Float)

    questions = db.relationship(
        "Question", backref="exam", cascade="all, delete-orphan", lazy="dynamic"
    )
    results = db.relationship(
        "Result", backref="exam", cascade="all, delete-orphan", lazy="dynamic"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "subject": self.subject,
            "date": self.date,
            "total_marks": self.total_marks,
        }


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_choices_number = db.Column(db.Integer, nullable=False)
    marks = db.Column(db.Float, nullable=False)

    choices = db.relationship(
        "Choice", backref="question", cascade="all, delete-orphan", lazy="dynamic"
    )
    answers = db.relationship(
        "StudentAnswer", backref="question", cascade="all, delete-orphan", lazy="dynamic"
    )

    def to_dict(self, include_choices=False):
        data = {
            "id": self.id,
            "exam_id": self.exam_id,
            "question_text": self.question_text,
            "choices_number": self.question_choices_number,
            "marks": self.marks,
        }
        if include_choices:
            data["choices"] = [c.to_dict() for c in self.choices.order_by(Choice.choice_label)]
        return data


class Choice(db.Model):
    __tablename__ = "choices"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    choice_label = db.Column(db.String(5), nullable=False)
    choice_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.choice_label,
            "text": self.choice_text,
            "is_correct": bool(self.is_correct),
        }
