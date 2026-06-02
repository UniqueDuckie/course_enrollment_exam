"""Create the SQL schema for the Course Enrollment Platform API.

Usage:
    python scripts/init_db.py
    python scripts/init_db.py --reset
    python scripts/init_db.py --db custom.db
"""

import argparse
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path("enrollment.db")

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT    NOT NULL CHECK (length(trim(name)) > 0),
        email           TEXT    NOT NULL UNIQUE
                               CHECK (email LIKE '_%@_%._%'),
        hashed_password TEXT    NOT NULL CHECK (length(hashed_password) > 0),
        role            TEXT    NOT NULL CHECK (role IN ('student', 'admin')),
        is_active       INTEGER NOT NULL DEFAULT 1
                               CHECK (is_active IN (0, 1))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS courses (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        title     TEXT    NOT NULL CHECK (length(trim(title)) > 0),
        code      TEXT    NOT NULL UNIQUE
                         CHECK (length(trim(code)) > 0),
        capacity  INTEGER NOT NULL CHECK (capacity > 0),
        is_active INTEGER NOT NULL DEFAULT 1
                         CHECK (is_active IN (0, 1))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS enrollments (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL,
        course_id  INTEGER NOT NULL,
        created_at TEXT    NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
        UNIQUE (user_id, course_id)
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_enrollments_user_id   ON enrollments(user_id);",
    "CREATE INDEX IF NOT EXISTS ix_enrollments_course_id ON enrollments(course_id);",
]

DROP = [
    "DROP TABLE IF EXISTS enrollments;",
    "DROP TABLE IF EXISTS courses;",
    "DROP TABLE IF EXISTS users;",
]


def init_db(db_path: Path, reset: bool) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.cursor()
        if reset:
            for stmt in DROP:
                cur.execute(stmt)
        for stmt in SCHEMA:
            cur.executescript(stmt)
        conn.commit()
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB,
                        help=f"SQLite file path (default: {DEFAULT_DB})")
    parser.add_argument("--reset", action="store_true",
                        help="Drop existing tables before creating")
    args = parser.parse_args()

    init_db(args.db, args.reset)
    print(f"Schema ready at: {args.db.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
