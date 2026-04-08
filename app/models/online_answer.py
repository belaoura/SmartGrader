"""Online answer model."""

from app.models import db


class OnlineAnswer(db.Model):
    __tablename__ = "online_answers"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("exam_attempts.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    selected_choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"), nullable=True)
    answered_at = db.Column(db.String(30))

    question = db.relationship("Question")
    selected_choice = db.relationship("Choice")

    __table_args__ = (
        db.UniqueConstraint("attempt_id", "question_id", name="uq_answer_attempt_question"),
    )
