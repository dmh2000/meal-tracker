from datetime import datetime, date
from zoneinfo import ZoneInfo
from flask import Blueprint, request, jsonify, g

from auth import login_required
from database import query_db, execute_db, get_db

log_bp = Blueprint("log", __name__, url_prefix="/api/log")

PACIFIC_TZ = ZoneInfo("America/Los_Angeles")
MEAL_TYPES = ["breakfast", "morning_snack", "lunch", "afternoon_snack", "dinner", "evening_snack"]


def get_pacific_today() -> date:
    """Get today's date in Pacific Time."""
    return datetime.now(PACIFIC_TZ).date()


def get_log_entry_with_items(log_id: int) -> dict | None:
    """Get a log entry with its items and total calories."""
    log = query_db(
        """
        SELECT l.id, l.meal_date, l.meal_type, l.meal_id, m.name as meal_name
        FROM user_meal_log l
        LEFT JOIN meals m ON m.id = l.meal_id
        WHERE l.id = ?
        """,
        (log_id,),
        one=True
    )

    if not log:
        return None

    items = query_db(
        """
        SELECT li.id, li.food_id, f.name as food_name, f.calories, li.quantity
        FROM user_meal_log_items li
        JOIN foods f ON f.id = li.food_id
        WHERE li.log_id = ?
        """,
        (log_id,)
    )

    items_list = [dict(i) for i in items]
    total_calories = sum(i["calories"] * i["quantity"] for i in items_list)

    return {
        "id": log["id"],
        "meal_date": log["meal_date"],
        "meal_type": log["meal_type"],
        "meal_id": log["meal_id"],
        "meal_name": log["meal_name"],
        "items": items_list,
        "total_calories": total_calories
    }


@log_bp.route("", methods=["GET"])
@login_required
def get_daily_log():
    """Get user's meal log for a specific date."""
    date_str = request.args.get("date", get_pacific_today().isoformat())

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    user_id = g.user["id"]

    logs = query_db(
        """
        SELECT l.id, l.meal_type, l.meal_id, m.name as meal_name
        FROM user_meal_log l
        LEFT JOIN meals m ON m.id = l.meal_id
        WHERE l.user_id = ? AND l.meal_date = ?
        """,
        (user_id, date_str)
    )

    logs_by_type = {log["meal_type"]: log for log in logs}

    meals_data = {}
    total_calories = 0

    for meal_type in MEAL_TYPES:
        log = logs_by_type.get(meal_type)

        if log:
            items = query_db(
                """
                SELECT li.id, li.food_id, f.name as food_name, f.calories, li.quantity
                FROM user_meal_log_items li
                JOIN foods f ON f.id = li.food_id
                WHERE li.log_id = ?
                """,
                (log["id"],)
            )

            items_list = [dict(i) for i in items]
            calories = sum(i["calories"] * i["quantity"] for i in items_list)
            total_calories += calories

            meals_data[meal_type] = {
                "log_id": log["id"],
                "meal_name": log["meal_name"],
                "items": items_list,
                "calories": calories
            }
        else:
            meals_data[meal_type] = {
                "log_id": None,
                "meal_name": None,
                "items": [],
                "calories": 0
            }

    return jsonify({
        "date": date_str,
        "total_calories": total_calories,
        "meals": meals_data
    })


@log_bp.route("/dates", methods=["GET"])
@login_required
def get_available_dates():
    """Get list of dates where the user has meal data."""
    user_id = g.user["id"]

    dates = query_db(
        """
        SELECT DISTINCT meal_date
        FROM user_meal_log
        WHERE user_id = ?
        ORDER BY meal_date ASC
        """,
        (user_id,)
    )

    return jsonify({
        "dates": [d["meal_date"] for d in dates]
    })


@log_bp.route("/<int:log_id>", methods=["GET"])
@login_required
def get_log_entry(log_id: int):
    """Get a specific meal log entry."""
    log = query_db(
        "SELECT user_id FROM user_meal_log WHERE id = ?",
        (log_id,),
        one=True
    )

    if not log:
        return jsonify({"error": "Log entry not found"}), 404

    if log["user_id"] != g.user["id"]:
        return jsonify({"error": "Not authorized"}), 403

    log_data = get_log_entry_with_items(log_id)
    return jsonify(log_data)


@log_bp.route("", methods=["POST"])
@login_required
def create_or_update_log():
    """Create or update a meal log entry for the current date."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body required"}), 400

    meal_type = (data.get("meal_type") or "").strip()
    meal_date = data.get("meal_date") or get_pacific_today().isoformat()
    meal_name_raw = data.get("meal_name")
    meal_name = meal_name_raw.strip() if meal_name_raw else None
    items = data.get("items") or []

    if meal_type not in MEAL_TYPES:
        return jsonify({"error": f"Invalid meal type. Must be one of: {', '.join(MEAL_TYPES)}"}), 400

    try:
        parsed_date = datetime.strptime(meal_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Allow logging meals for any date (removed current-date-only restriction)

    user_id = g.user["id"]
    meal_id = None

    conn = get_db()
    try:
        if meal_name:
            existing_meal = conn.execute(
                "SELECT id FROM meals WHERE name = ?",
                (meal_name,)
            ).fetchone()

            if existing_meal:
                meal_id = existing_meal["id"]
            else:
                cur = conn.execute(
                    "INSERT INTO meals (name, description) VALUES (?, ?)",
                    (meal_name, None)
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

        existing_log = conn.execute(
            "SELECT id FROM user_meal_log WHERE user_id = ? AND meal_date = ? AND meal_type = ?",
            (user_id, meal_date, meal_type)
        ).fetchone()

        if existing_log:
            log_id = existing_log["id"]

            conn.execute(
                "UPDATE user_meal_log SET meal_id = ?, updated_at = ? WHERE id = ?",
                (meal_id, datetime.now(PACIFIC_TZ).isoformat(), log_id)
            )

            conn.execute("DELETE FROM user_meal_log_items WHERE log_id = ?", (log_id,))
        else:
            cur = conn.execute(
                "INSERT INTO user_meal_log (user_id, meal_date, meal_type, meal_id) VALUES (?, ?, ?, ?)",
                (user_id, meal_date, meal_type, meal_id)
            )
            log_id = cur.lastrowid

        for item in items:
            food_id = item.get("food_id")
            quantity = item.get("quantity", 1.0)
            if food_id:
                conn.execute(
                    "INSERT INTO user_meal_log_items (log_id, food_id, quantity) VALUES (?, ?, ?)",
                    (log_id, food_id, quantity)
                )

        conn.commit()
    finally:
        conn.close()

    return jsonify(get_log_entry_with_items(log_id)), 201


@log_bp.route("/<int:log_id>", methods=["DELETE"])
@login_required
def delete_log_entry(log_id: int):
    """Delete a meal log entry (only allowed for current date)."""
    log = query_db(
        "SELECT user_id, meal_date FROM user_meal_log WHERE id = ?",
        (log_id,),
        one=True
    )

    if not log:
        return jsonify({"error": "Log entry not found"}), 404

    if log["user_id"] != g.user["id"]:
        return jsonify({"error": "Not authorized"}), 403

    # Allow deleting meals for any date (removed current-date-only restriction)

    execute_db("DELETE FROM user_meal_log WHERE id = ?", (log_id,))

    return jsonify({"success": True})
