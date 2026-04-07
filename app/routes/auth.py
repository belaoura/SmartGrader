"""Authentication API endpoints."""

import logging
from flask import Blueprint, request, jsonify, make_response, current_app, g

from app.auth import require_auth, set_auth_cookies, clear_auth_cookies, decode_token, encode_access_token
from app.services.auth_service import login_teacher, login_student, logout_user
from app.models.user import User
from app import limiter

logger = logging.getLogger("smartgrader.routes.auth")
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """Teacher login with email and password."""
    data = request.get_json()
    email = data.get("email", "")
    password = data.get("password", "")

    user = login_teacher(email, password)

    response = make_response(jsonify({"user": user.to_dict()}))
    set_auth_cookies(response, user)
    return response


@auth_bp.route("/auth/scan", methods=["POST"])
@limiter.limit("5 per minute")
def scan_login():
    """Student login via barcode scan (matricule)."""
    data = request.get_json()
    matricule = data.get("matricule", "")

    user = login_student(matricule)

    response = make_response(jsonify({"user": user.to_dict()}))
    set_auth_cookies(response, user)
    return response


@auth_bp.route("/auth/refresh", methods=["POST"])
def refresh():
    """Refresh access token using refresh cookie."""
    token = request.cookies.get("refresh_token")
    if not token:
        return jsonify({"error": "Refresh token required"}), 401

    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        return jsonify({"error": "Invalid refresh token"}), 401

    user = User.query.get(int(payload["sub"]))
    if not user or not user.is_active:
        return jsonify({"error": "User not found or disabled"}), 401
    if user.token_version != payload.get("ver"):
        return jsonify({"error": "Session expired"}), 401

    access_token = encode_access_token(user)
    is_secure = (
        not current_app.config.get("DEBUG", False)
        and not current_app.config.get("TESTING", False)
    )

    response = make_response(jsonify({"message": "Token refreshed"}))
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=is_secure,
        samesite="Lax",
        max_age=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
        path="/",
    )
    return response


@auth_bp.route("/auth/logout", methods=["POST"])
@require_auth
def logout():
    """Log out the current user (invalidate tokens)."""
    logout_user(g.current_user.id)

    response = make_response(jsonify({"message": "Logged out"}))
    clear_auth_cookies(response)
    return response


@auth_bp.route("/auth/me", methods=["GET"])
@require_auth
def me():
    """Get current authenticated user info."""
    return jsonify({"user": g.current_user.to_dict()})
