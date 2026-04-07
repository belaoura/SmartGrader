"""JWT helpers and authentication decorators."""

import logging
from datetime import datetime, timezone, timedelta
from functools import wraps

import jwt
from flask import request, g, current_app, jsonify

from app.models.user import User

logger = logging.getLogger("smartgrader.auth")


def encode_access_token(user):
    """Create a short-lived access JWT for the given user."""
    payload = {
        "sub": user.id,
        "role": user.role,
        "ver": user.token_version,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(
            seconds=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        ),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def encode_refresh_token(user):
    """Create a long-lived refresh JWT for the given user."""
    payload = {
        "sub": user.id,
        "ver": user.token_version,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(
            seconds=current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
        ),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token):
    """Decode and verify a JWT. Returns the payload dict or None."""
    try:
        return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        logger.debug("Token expired")
        return None
    except jwt.InvalidTokenError:
        logger.debug("Invalid token")
        return None


def set_auth_cookies(response, user):
    """Set access and refresh token cookies on a response."""
    access_token = encode_access_token(user)
    refresh_token = encode_refresh_token(user)

    is_prod = not current_app.config.get("DEBUG", False)

    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=is_prod,
        samesite="Lax",
        max_age=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=is_prod,
        samesite="Lax",
        max_age=current_app.config["JWT_REFRESH_TOKEN_EXPIRES"],
        path="/api/auth/refresh",
    )
    return response


def clear_auth_cookies(response):
    """Remove auth cookies from a response."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/auth/refresh")
    return response


def require_auth(f):
    """Decorator: require a valid access token. Sets g.current_user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return jsonify({"error": "Authentication required"}), 401

        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return jsonify({"error": "Invalid or expired token"}), 401

        user = User.query.get(payload["sub"])
        if not user:
            return jsonify({"error": "User not found"}), 401
        if not user.is_active:
            return jsonify({"error": "Account is disabled"}), 401
        if user.token_version != payload.get("ver"):
            return jsonify({"error": "Session expired"}), 401

        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def require_role(role_name):
    """Decorator factory: require a specific role. Must be used after @require_auth."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.current_user.role != role_name:
                return jsonify({"error": "Permission denied"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def require_admin(f):
    """Decorator: require admin flag. Must be used after @require_auth."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated
