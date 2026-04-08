"""Tests for group service."""

import pytest
from app.models.student import Student
from app.models.group import StudentGroup, StudentGroupMember
from app.services.group_service import (
    create_group, get_all_groups, get_group_by_id,
    delete_group, add_members, remove_member,
)
from app.errors import NotFoundError


def test_create_group(db):
    group = create_group("CS Year 3")
    assert group.id is not None
    assert group.name == "CS Year 3"


def test_get_all_groups(db):
    create_group("G1")
    create_group("G2")
    groups = get_all_groups()
    assert len(groups) == 2


def test_get_group_by_id(db):
    group = create_group("G1")
    found = get_group_by_id(group.id)
    assert found.name == "G1"


def test_get_group_not_found(db):
    with pytest.raises(NotFoundError):
        get_group_by_id(999)


def test_delete_group(db):
    group = create_group("Del")
    delete_group(group.id)
    assert StudentGroup.query.count() == 0


def test_add_members(db):
    group = create_group("G1")
    s1 = Student(name="A", matricule="001")
    s2 = Student(name="B", matricule="002")
    db.session.add_all([s1, s2])
    db.session.commit()
    count = add_members(group.id, [s1.id, s2.id])
    assert count == 2
    assert group.members.count() == 2


def test_add_members_skip_duplicates(db):
    group = create_group("G1")
    s1 = Student(name="A", matricule="001")
    db.session.add(s1)
    db.session.commit()
    add_members(group.id, [s1.id])
    count = add_members(group.id, [s1.id])
    assert count == 0
    assert group.members.count() == 1


def test_remove_member(db):
    group = create_group("G1")
    s1 = Student(name="A", matricule="001")
    db.session.add(s1)
    db.session.commit()
    add_members(group.id, [s1.id])
    remove_member(group.id, s1.id)
    assert group.members.count() == 0
