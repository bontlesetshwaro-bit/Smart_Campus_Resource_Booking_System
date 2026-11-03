import sqlite3
import hashlib
from rules import CAMPUS_RULES

DB_FILE = "campus_booking.db"


def run(sql, params=(), fetch=False):
    """Run one SQL command. Returns rows if fetch=True."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cur = conn.execute(sql, params)
        rows = cur.fetchall() if fetch else None
        conn.commit()
        return rows
    finally:
        conn.close()


def hash_password(password):
    """Passwords are never stored as plain text."""
    return hashlib.sha256(password.encode()).hexdigest()


def setup_database():
    """Create tables (first run only) and add starting data."""
    run("""CREATE TABLE IF NOT EXISTS campuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL)""")
    run("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            campus_id INTEGER)""")
    run("""CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            campus_id INTEGER NOT NULL)""")
    run("""CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            campus_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            start TEXT NOT NULL,
            duration INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active')""")

    # Campuses come from the CAMPUS_RULES dictionary
    for name in CAMPUS_RULES:
        run("INSERT OR IGNORE INTO campuses (name) VALUES (?)", (name,))

    # Default accounts (only created if they do not exist yet)
    run("INSERT OR IGNORE INTO users (username, password, role, campus_id) "
        "VALUES (?, ?, 'System Operator', NULL)",
        ("operator", hash_password("operator123")))
    for cid, name in run("SELECT id, name FROM campuses", fetch=True):
        run("INSERT OR IGNORE INTO users (username, password, role, campus_id) "
            "VALUES (?, ?, 'Campus Admin', ?)",
            ("admin_" + name.lower(), hash_password("admin123"), cid))
        # a few starting resources per campus
        prefix = name[:3].upper()
        for code, rname in [(prefix + "-LAB1", "Computer Lab 1"),
                            (prefix + "-PROJ1", "Projector 1"),
                            (prefix + "-SEM1", "Seminar Room 1")]:
            run("INSERT OR IGNORE INTO resources (code, name, campus_id) "
                "VALUES (?, ?, ?)", (code, rname, cid))
