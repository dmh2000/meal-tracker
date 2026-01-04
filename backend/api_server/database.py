import sqlite3
import os
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent.parent / "db" / "meals.db"
SCHEMA_PATH = Path(__file__).parent.parent.parent / "db" / "schema.sql"


def get_db() -> sqlite3.Connection:
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize the database with the schema if it doesn't exist."""
    if DATABASE_PATH.exists():
        return

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()

    conn = get_db()
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


def query_db(query: str, args: tuple = (), one: bool = False):
    """Execute a query and return results."""
    conn = get_db()
    try:
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv
    finally:
        conn.close()


def execute_db(query: str, args: tuple = ()) -> int:
    """Execute a query and return the last row id."""
    conn = get_db()
    try:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def execute_many_db(query: str, args_list: list) -> None:
    """Execute a query with multiple sets of arguments."""
    conn = get_db()
    try:
        conn.executemany(query, args_list)
        conn.commit()
    finally:
        conn.close()
