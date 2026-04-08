"""Student group models."""

from datetime import datetime, timezone
from app.models import db


class StudentGroup(db.Model):
    __tablename__ = "student_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.String(30), default=lambda: datetime.now(timezone.utc).isoformat())

    members = db.relationship(
        "StudentGroupMember", backref="group", cascade="all, delete-orphan", lazy="dynamic"
    )

    def to_dict(self, include_members=False):
        data = {
            "id": self.id,
            "name": self.name,
            "member_count": self.members.count(),
            "created_at": self.created_at,
        }
        if include_members:
            data["members"] = [
                {"id": m.student.id, "name": m.student.name, "matricule": m.student.matricule}
                for m in self.members.all()
            ]
        return data


class StudentGroupMember(db.Model):
    __tablename__ = "student_group_members"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("student_groups.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)

    student = db.relationship("Student")

    __table_args__ = (
        db.UniqueConstraint("group_id", "student_id", name="uq_group_student"),
    )
