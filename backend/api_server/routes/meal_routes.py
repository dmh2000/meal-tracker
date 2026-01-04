from flask import Blueprint, request, jsonify

from auth import login_required
from database import query_db, execute_db, get_db

meal_bp = Blueprint("meals", __name__, url_prefix="/api/meals")


def get_meal_with_items(meal_id: int) -> dict | None:
    """Get a meal with its items and total calories."""
    meal = query_db(
        "SELECT id, name, description FROM meals WHERE id = ?",
        (meal_id,),
        one=True
    )

    if not meal:
        return None

    items = query_db(
        """
        SELECT mi.id, mi.food_id, f.name as food_name, f.calories, mi.quantity
        FROM meal_items mi
        JOIN foods f ON f.id = mi.food_id
        WHERE mi.meal_id = ?
        """,
        (meal_id,)
    )

    items_list = [dict(i) for i in items]
    total_calories = sum(i["calories"] * i["quantity"] for i in items_list)

    return {
        "id": meal["id"],
        "name": meal["name"],
        "description": meal["description"],
        "items": items_list,
        "total_calories": total_calories
    }


@meal_bp.route("", methods=["GET"])
@login_required
def get_meals():
    """Get all meal templates (only those with descriptions)."""
    meals = query_db(
        "SELECT id, name, description FROM meals WHERE description IS NOT NULL AND description != '' ORDER BY name"
    )

    result = []
    for meal in meals:
        meal_data = get_meal_with_items(meal["id"])
        if meal_data:
            result.append(meal_data)

    return jsonify(result)


@meal_bp.route("/<int:meal_id>", methods=["GET"])
@login_required
def get_meal(meal_id: int):
    """Get a specific meal template."""
    meal_data = get_meal_with_items(meal_id)

    if not meal_data:
        return jsonify({"error": "Meal not found"}), 404

    return jsonify(meal_data)


@meal_bp.route("", methods=["POST"])
@login_required
def create_meal():
    """Create a new meal template."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body required"}), 400

    name = data.get("name", "").strip()
    description = data.get("description", "").strip() or None
    items = data.get("items", [])

    if not name:
        return jsonify({"error": "Meal name is required"}), 400

    existing = query_db(
        "SELECT id FROM meals WHERE name = ?",
        (name,),
        one=True
    )

    if existing:
        return jsonify({"error": "Meal with this name already exists"}), 400

    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO meals (name, description) VALUES (?, ?)",
            (name, description)
        )
        meal_id = cur.lastrowid

        for item in items:
            food_id = item.get("food_id")
            quantity = item.get("quantity", 1.0)

            if food_id:
                conn.execute(
                    "INSERT INTO meal_items (meal_id, food_id, quantity) VALUES (?, ?, ?)",
                    (meal_id, food_id, quantity)
                )

        conn.commit()
    finally:
        conn.close()

    return jsonify(get_meal_with_items(meal_id)), 201
