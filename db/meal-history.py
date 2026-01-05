#!/usr/bin/env python3
"""Print meal history for a specified user."""

import argparse
import sqlite3
import sys
from pathlib import Path

MEAL_TYPE_ORDER = [
    'breakfast',
    'morning_snack',
    'lunch',
    'afternoon_snack',
    'dinner',
    'evening_snack'
]

MEAL_TYPE_LABELS = {
    'breakfast': 'Breakfast',
    'morning_snack': 'Morning Snack',
    'lunch': 'Lunch',
    'afternoon_snack': 'Afternoon Snack',
    'dinner': 'Dinner',
    'evening_snack': 'Evening Snack'
}


def get_user_id(cursor, username):
    """Get user ID from username."""
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    return row[0] if row else None


def get_meal_history(cursor, user_id):
    """Get all meal log entries for a user, ordered by date and meal type."""
    cursor.execute("""
        SELECT
            l.id,
            l.meal_date,
            l.meal_type,
            m.name as meal_name
        FROM user_meal_log l
        LEFT JOIN meals m ON m.id = l.meal_id
        WHERE l.user_id = ?
        ORDER BY l.meal_date DESC, l.meal_type
    """, (user_id,))
    return cursor.fetchall()


def get_meal_items(cursor, log_id):
    """Get all food items for a meal log entry."""
    cursor.execute("""
        SELECT
            f.name,
            f.calories,
            li.quantity
        FROM user_meal_log_items li
        JOIN foods f ON f.id = li.food_id
        WHERE li.log_id = ?
        ORDER BY f.name
    """, (log_id,))
    return cursor.fetchall()


def format_date(date_str):
    """Format date string for display."""
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%A, %B %d, %Y")
    except ValueError:
        return date_str


def main():
    parser = argparse.ArgumentParser(
        description="Print meal history for a specified user"
    )
    parser.add_argument("username", help="Username to show history for")
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=0,
        help="Limit to last N days (0 = all history)"
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Output in CSV format"
    )
    args = parser.parse_args()

    db_path = Path(__file__).parent / "meals.db"

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Look up user
    user_id = get_user_id(cursor, args.username)
    if not user_id:
        print(f"Error: User '{args.username}' not found", file=sys.stderr)
        conn.close()
        sys.exit(1)

    # Get meal history
    logs = get_meal_history(cursor, user_id)

    if not logs:
        print(f"No meal history found for user '{args.username}'")
        conn.close()
        return

    # Filter by days if specified
    if args.days > 0:
        from datetime import datetime, timedelta
        cutoff = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
        logs = [log for log in logs if log['meal_date'] >= cutoff]

    if args.csv:
        # CSV output
        import csv
        writer = csv.writer(sys.stdout)
        writer.writerow(["date", "meal_type", "meal_name", "food_name", "calories", "quantity", "total_calories"])

        for log in logs:
            items = get_meal_items(cursor, log['id'])
            if items:
                for item in items:
                    total_cal = int(item['calories'] * item['quantity'])
                    writer.writerow([
                        log['meal_date'],
                        log['meal_type'],
                        log['meal_name'] or '',
                        item['name'],
                        item['calories'],
                        item['quantity'],
                        total_cal
                    ])
            else:
                writer.writerow([
                    log['meal_date'],
                    log['meal_type'],
                    log['meal_name'] or '',
                    '',
                    0,
                    0,
                    0
                ])
    else:
        # Human-readable output
        print(f"Meal History for {args.username}")
        print("=" * 60)

        current_date = None
        daily_total = 0

        for log in logs:
            # Print date header when date changes
            if log['meal_date'] != current_date:
                if current_date is not None:
                    print(f"  {'Daily Total:':<40} {daily_total:>6} cal")
                    print()

                current_date = log['meal_date']
                daily_total = 0
                print(f"\n{format_date(current_date)}")
                print("-" * 60)

            # Get items for this meal
            items = get_meal_items(cursor, log['id'])
            meal_calories = sum(int(i['calories'] * i['quantity']) for i in items)
            daily_total += meal_calories

            # Print meal header
            meal_label = MEAL_TYPE_LABELS.get(log['meal_type'], log['meal_type'])
            meal_name = f" - {log['meal_name']}" if log['meal_name'] else ""
            print(f"\n  {meal_label}{meal_name} ({meal_calories} cal)")

            # Print items
            if items:
                for item in items:
                    qty_str = f"x{item['quantity']}" if item['quantity'] != 1 else ""
                    item_cal = int(item['calories'] * item['quantity'])
                    print(f"    - {item['name']:<32} {qty_str:>4} {item_cal:>6} cal")
            else:
                print("    (no items)")

        # Print final daily total
        if current_date is not None:
            print(f"\n  {'Daily Total:':<40} {daily_total:>6} cal")

        print("\n" + "=" * 60)

    conn.close()


if __name__ == "__main__":
    main()
