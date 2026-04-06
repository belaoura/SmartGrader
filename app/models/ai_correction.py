"""AICorrection model for RAG feedback loop."""

from app.models import db


class AICorrection(db.Model):
    __tablename__ = "ai_corrections"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    student_text = db.Column(db.Text, nullable=False)
    ai_score = db.Column(db.Float, nullable=False)
    ai_feedback = db.Column(db.Text)
    teacher_score = db.Column(db.Float, nullable=False)
    teacher_feedback = db.Column(db.Text)
    created_at = db.Column(db.String(30), nullable=False)

    question = db.relationship("Question", backref="ai_corrections")

    def to_dict(self):
        return {
            "id": self.id,
            "question_id": self.question_id,
            "student_text": self.student_text,
            "ai_score": self.ai_score,
            "ai_feedback": self.ai_feedback,
            "teacher_score": self.teacher_score,
            "teacher_feedback": self.teacher_feedback,
            "created_at": self.created_at,
        }
