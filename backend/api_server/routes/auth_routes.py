from flask import Blueprint, request, jsonify, g, make_response

from auth import (
    hash_password,
    verify_password,
    create_session_token,
    invalidate_session_token,
    login_required,
)
from database import query_db, execute_db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body required"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400

    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    existing = query_db(
        "SELECT id FROM users WHERE username = ?",
        (username,),
        one=True
    )

    if existing:
        return jsonify({"error": "Username already exists"}), 400

    password_hash, password_salt = hash_password(password)

    user_id = execute_db(
        "INSERT INTO users (username, password_hash, password_salt) VALUES (?, ?, ?)",
        (username, password_hash, password_salt)
    )

    return jsonify({"id": user_id, "username": username}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login and create session."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body required"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")
    remember_me = data.get("remember_me", False)

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = query_db(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
        one=True
    )

    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    if not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_session_token(user["id"], remember_me)

    response = make_response(jsonify({
        "id": user["id"],
        "username": user["username"]
    }))

    max_age = 30 * 24 * 60 * 60 if remember_me else 24 * 60 * 60
    response.set_cookie(
        "session_token",
        token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="Lax",
        max_age=max_age
    )

    return response


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Logout and invalidate session."""
    token = request.cookies.get("session_token")

    if token:
        invalidate_session_token(token)

    response = make_response(jsonify({"success": True}))
    response.delete_cookie("session_token")

    return response


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    """Get current authenticated user."""
    return jsonify(g.user)
