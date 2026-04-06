"""Result model for exam scores."""

from app.models import db


class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)
    percentage = db.Column(db.Float)
    graded_at = db.Column(db.String(30))

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "exam_id": self.exam_id,
            "score": self.score,
            "percentage": self.percentage,
            "graded_at": self.graded_at,
            "student_name": self.student.name if self.student else None,
            "exam_title": self.exam.title if self.exam else None,
        }
