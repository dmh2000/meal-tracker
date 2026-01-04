import logging
from flask import Blueprint, request, jsonify, g, make_response

from auth import (
    create_session_token,
    invalidate_session_token,
    login_required,
)
from database import query_db, execute_db

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user with just a username."""
    logger.info("Register endpoint called")
    data = request.get_json()

    if not data:
        logger.warning("Register: No request body")
        return jsonify({"error": "Request body required"}), 400

    username = data.get("username", "").strip()
    logger.info(f"Register: username='{username}'")

    if not username or len(username) < 1:
        logger.warning("Register: Username is required")
        return jsonify({"error": "Username is required"}), 400

    existing = query_db(
        "SELECT id FROM users WHERE username = ?",
        (username,),
        one=True
    )

    if existing:
        logger.warning(f"Register: Username '{username}' already exists")
        return jsonify({"error": "Username already exists"}), 400

    user_id = execute_db(
        "INSERT INTO users (username) VALUES (?)",
        (username,)
    )
    logger.info(f"Register: Created user id={user_id}")

    token = create_session_token(user_id, remember_me=True)
    logger.info(f"Register: Created session token for user id={user_id}")

    response = make_response(jsonify({"id": user_id, "username": username}), 201)

    response.set_cookie(
        "session_token",
        token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=30 * 24 * 60 * 60
    )

    logger.info(f"Register: Success for '{username}'")
    return response


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login with just a username."""
    logger.info("Login endpoint called")
    data = request.get_json()

    if not data:
        logger.warning("Login: No request body")
        return jsonify({"error": "Request body required"}), 400

    username = data.get("username", "").strip()
    remember_me = data.get("remember_me", True)
    logger.info(f"Login: username='{username}', remember_me={remember_me}")

    if not username:
        logger.warning("Login: Username is required")
        return jsonify({"error": "Username is required"}), 400

    user = query_db(
        "SELECT id, username FROM users WHERE username = ?",
        (username,),
        one=True
    )

    if not user:
        logger.warning(f"Login: User '{username}' not found")
        return jsonify({"error": "User not found"}), 401

    logger.info(f"Login: Found user id={user['id']}")
    token = create_session_token(user["id"], remember_me)
    logger.info(f"Login: Created session token for user id={user['id']}")

    response = make_response(jsonify({
        "id": user["id"],
        "username": user["username"]
    }))

    max_age = 30 * 24 * 60 * 60 if remember_me else 24 * 60 * 60
    response.set_cookie(
        "session_token",
        token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=max_age
    )

    logger.info(f"Login: Success for '{username}'")
    return response


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Logout and invalidate session."""
    logger.info("Logout endpoint called")
    token = request.cookies.get("session_token")

    if token:
        invalidate_session_token(token)
        logger.info("Logout: Session invalidated")
    else:
        logger.info("Logout: No session token found")

    response = make_response(jsonify({"success": True}))
    response.delete_cookie("session_token")

    return response


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    """Get current authenticated user."""
    logger.info(f"Me endpoint: user={g.user}")
    return jsonify(g.user)
