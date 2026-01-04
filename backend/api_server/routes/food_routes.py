from flask import Blueprint, request, jsonify

from auth import login_required
from database import query_db, execute_db

food_bp = Blueprint("foods", __name__, url_prefix="/api/foods")


@food_bp.route("", methods=["GET"])
@login_required
def get_foods():
    """Get all food items."""
    foods = query_db("SELECT id, name, calories FROM foods ORDER BY name")
    return jsonify([dict(f) for f in foods])


@food_bp.route("/search", methods=["GET"])
@login_required
def search_foods():
    """Search foods by name."""
    q = request.args.get("q", "").strip()

    if not q:
        return jsonify([])

    foods = query_db(
        "SELECT id, name, calories FROM foods WHERE name LIKE ? ORDER BY name LIMIT 20",
        (f"%{q}%",)
    )

    return jsonify([dict(f) for f in foods])


@food_bp.route("", methods=["POST"])
@login_required
def create_food():
    """Create a new food item."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body required"}), 400

    name = data.get("name", "").strip()
    calories = data.get("calories")

    if not name:
        return jsonify({"error": "Food name is required"}), 400

    if calories is None or not isinstance(calories, (int, float)) or calories < 0:
        return jsonify({"error": "Valid calorie count is required"}), 400

    existing = query_db(
        "SELECT id FROM foods WHERE name = ?",
        (name,),
        one=True
    )

    if existing:
        return jsonify({"error": "Food with this name already exists"}), 400

    food_id = execute_db(
        "INSERT INTO foods (name, calories) VALUES (?, ?)",
        (name, int(calories))
    )

    return jsonify({"id": food_id, "name": name, "calories": int(calories)}), 201
