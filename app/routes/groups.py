"""Student group API endpoints."""

import logging
from flask import Blueprint, request, jsonify
from app.auth import require_auth, require_role
from app.services.group_service import (
    create_group, get_all_groups, get_group_by_id,
    delete_group, add_members, remove_member,
)

logger = logging.getLogger("smartgrader.routes.groups")
groups_bp = Blueprint("groups", __name__)


@groups_bp.route("/groups", methods=["POST"])
@require_auth
@require_role("teacher")
def create():
    data = request.get_json()
    group = create_group(name=data["name"])
    return jsonify(group.to_dict()), 201


@groups_bp.route("/groups", methods=["GET"])
@require_auth
@require_role("teacher")
def list_all():
    groups = get_all_groups()
    return jsonify([g.to_dict() for g in groups])


@groups_bp.route("/groups/<int:group_id>", methods=["GET"])
@require_auth
@require_role("teacher")
def get_one(group_id):
    group = get_group_by_id(group_id)
    return jsonify(group.to_dict(include_members=True))


@groups_bp.route("/groups/<int:group_id>", methods=["DELETE"])
@require_auth
@require_role("teacher")
def delete(group_id):
    delete_group(group_id)
    return jsonify({"message": "Group deleted"})


@groups_bp.route("/groups/<int:group_id>/members", methods=["POST"])
@require_auth
@require_role("teacher")
def add(group_id):
    data = request.get_json()
    count = add_members(group_id, data["student_ids"])
    return jsonify({"added": count})


@groups_bp.route("/groups/<int:group_id>/members/<int:student_id>", methods=["DELETE"])
@require_auth
@require_role("teacher")
def remove(group_id, student_id):
    remove_member(group_id, student_id)
    return jsonify({"message": "Member removed"})
