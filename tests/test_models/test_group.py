"""Tests for StudentGroup and StudentGroupMember models."""

from app.models.group import StudentGroup, StudentGroupMember
from app.models.student import Student
from app.models import db as _db


def test_create_group(db):
    group = StudentGroup(name="CS Year 3 Group A")
    db.session.add(group)
    db.session.commit()
    assert group.id is not None
    assert group.name == "CS Year 3 Group A"
    assert group.created_at is not None


def test_add_member_to_group(db):
    group = StudentGroup(name="G1")
    student = Student(name="Ali", matricule="001")
    db.session.add_all([group, student])
    db.session.commit()
    member = StudentGroupMember(group_id=group.id, student_id=student.id)
    db.session.add(member)
    db.session.commit()
    assert member.id is not None
    assert group.members.count() == 1


def test_group_to_dict(db):
    group = StudentGroup(name="Test Group")
    db.session.add(group)
    db.session.commit()
    s1 = Student(name="A", matricule="001")
    s2 = Student(name="B", matricule="002")
    db.session.add_all([s1, s2])
    db.session.commit()
    db.session.add_all([
        StudentGroupMember(group_id=group.id, student_id=s1.id),
        StudentGroupMember(group_id=group.id, student_id=s2.id),
    ])
    db.session.commit()
    d = group.to_dict()
    assert d["name"] == "Test Group"
    assert d["member_count"] == 2
    d_full = group.to_dict(include_members=True)
    assert len(d_full["members"]) == 2


def test_group_cascade_delete(db):
    group = StudentGroup(name="Del")
    student = Student(name="X", matricule="099")
    db.session.add_all([group, student])
    db.session.commit()
    db.session.add(StudentGroupMember(group_id=group.id, student_id=student.id))
    db.session.commit()
    db.session.delete(group)
    db.session.commit()
    assert StudentGroupMember.query.count() == 0
    assert Student.query.count() == 1
