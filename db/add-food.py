#!/usr/bin/env python3
"""Add a new food entry to the meals database."""

import argparse
import sqlite3
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Add a new food to the database")
    parser.add_argument("name", help="Name of the food")
    parser.add_argument("calories", type=int, help="Calories per serving")
    args = parser.parse_args()

    db_path = Path(__file__).parent / "meals.db"

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}", file=sys.stderr)
        sys.exit(1)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO foods (name, calories) VALUES (?, ?)",
            (args.name, args.calories)
        )
        conn.commit()
        food_id = cursor.lastrowid
        print(f"Added food '{args.name}' ({args.calories} cal) with id {food_id}")
    except sqlite3.IntegrityError:
        print(f"Error: Food '{args.name}' already exists", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
