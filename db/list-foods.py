#!/usr/bin/env python3
"""Print all foods from the database in CSV format."""

import csv
import sqlite3
import sys
from pathlib import Path


def main():
    db_path = Path(__file__).parent / "meals.db"

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, calories, created_at FROM foods ORDER BY name")
    rows = cursor.fetchall()
    conn.close()

    writer = csv.writer(sys.stdout)
    writer.writerow(["id", "name", "calories", "created_at"])
    writer.writerows(rows)


if __name__ == "__main__":
    main()
