"""Student group management service."""

import logging
from app.models import db
from app.models.group import StudentGroup, StudentGroupMember
from app.errors import NotFoundError

logger = logging.getLogger("smartgrader.services.group")


def create_group(name):
    """Create a new student group."""
    group = StudentGroup(name=name)
    db.session.add(group)
    db.session.commit()
    logger.info("Created group: %s", name)
    return group


def get_all_groups():
    """List all student groups."""
    return StudentGroup.query.order_by(StudentGroup.name).all()


def get_group_by_id(group_id):
    """Get a group by ID. Raises NotFoundError if not found."""
    group = db.session.get(StudentGroup, group_id)
    if not group:
        raise NotFoundError("Group", group_id)
    return group


def delete_group(group_id):
    """Delete a group and all its memberships."""
    group = get_group_by_id(group_id)
    db.session.delete(group)
    db.session.commit()
    logger.info("Deleted group: %s", group_id)


def add_members(group_id, student_ids):
    """Add students to a group. Skips duplicates. Returns count added."""
    group = get_group_by_id(group_id)
    existing = {m.student_id for m in group.members.all()}
    added = 0
    for sid in student_ids:
        if sid not in existing:
            db.session.add(StudentGroupMember(group_id=group.id, student_id=sid))
            existing.add(sid)
            added += 1
    db.session.commit()
    logger.info("Added %d members to group %s", added, group_id)
    return added


def remove_member(group_id, student_id):
    """Remove a student from a group."""
    member = StudentGroupMember.query.filter_by(
        group_id=group_id, student_id=student_id
    ).first()
    if member:
        db.session.delete(member)
        db.session.commit()
        logger.info("Removed student %s from group %s", student_id, group_id)
