"""
booking.py - Everything about resources, bookings and reports.
These functions talk to the database. They never touch the screen.
"""

import sqlite3
from datetime import datetime
from database import run
from rules import check_booking_rules, to_minutes, policy_text


# ---------------- Bookings ----------------
def is_available(resource_id, date_text, start_text, duration):
    """True if no active booking overlaps the requested time."""
    new_start = to_minutes(start_text)
    new_end = new_start + duration
    rows = run("SELECT start, duration FROM bookings "
               "WHERE resource_id=? AND date=? AND status='Active'",
               (resource_id, date_text), fetch=True)
    for start, length in rows:
        old_start = to_minutes(start)
        old_end = old_start + length
        if new_start < old_end and old_start < new_end:
            return False
    return True


def booking_state(date_text, start_text, status):
    """Cancelled, Past or Upcoming."""
    if status == "Cancelled":
        return "Cancelled"
    start = datetime.strptime(date_text + " " + start_text, "%Y-%m-%d %H:%M")
    if start < datetime.now():
        return "Past"
    return "Upcoming"


def create_booking(user_id, campus_id, campus_name, resource_id,
                   date_text, start_text, duration):
    """Save a booking. Returns an error message, or None if it worked."""
    start = datetime.strptime(date_text + " " + start_text, "%Y-%m-%d %H:%M")
    if start < datetime.now():
        return "You cannot book a time that has already passed."
    error = check_booking_rules(campus_name, date_text, start_text, duration)
    if error:
        return error
    if not is_available(resource_id, date_text, start_text, duration):
        return "That resource is already booked for the chosen time."
    run("INSERT INTO bookings (resource_id, user_id, campus_id, date, start, duration) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (resource_id, user_id, campus_id, date_text, start_text, duration))
    return None


def get_user_bookings(user_id, show="All"):
    """Bookings of one lecturer. show = All, Upcoming, Past or Cancelled."""
    rows = run("SELECT b.id, c.name, r.name, b.date, b.start, b.duration, b.status "
               "FROM bookings b "
               "JOIN campuses c ON c.id = b.campus_id "
               "JOIN resources r ON r.id = b.resource_id "
               "WHERE b.user_id=? ORDER BY b.date DESC, b.start DESC",
               (user_id,), fetch=True)
    result = []
    for booking_id, campus, resource, date, start, duration, status in rows:
        state = booking_state(date, start, status)
        if show == "All" or show == state:
            result.append((booking_id, campus, resource, date, start, duration, state))
    return result


def cancel_booking(booking_id):
    """Cancel an upcoming booking. Returns an error message or None."""
    rows = run("SELECT date, start, status FROM bookings WHERE id=?",
               (booking_id,), fetch=True)
    if not rows:
        return "Booking not found."
    if booking_state(*rows[0]) != "Upcoming":
        return "Only upcoming bookings can be cancelled."
    run("UPDATE bookings SET status='Cancelled' WHERE id=?", (booking_id,))
    return None


def get_campus_bookings(campus_id):
    """All bookings of one campus (for the administrator)."""
    rows = run("SELECT r.name, u.username, b.date, b.start, b.duration, b.status "
               "FROM bookings b "
               "JOIN resources r ON r.id = b.resource_id "
               "JOIN users u ON u.id = b.user_id "
               "WHERE b.campus_id=? ORDER BY b.date DESC, b.start DESC",
               (campus_id,), fetch=True)
    return [(r, u, d, s, m, booking_state(d, s, st)) for r, u, d, s, m, st in rows]


def get_all_bookings():
    """Bookings of every campus (for the system operator)."""
    rows = run("SELECT c.name, r.name, u.username, b.date, b.start, b.duration, b.status "
               "FROM bookings b "
               "JOIN campuses c ON c.id = b.campus_id "
               "JOIN resources r ON r.id = b.resource_id "
               "JOIN users u ON u.id = b.user_id "
               "ORDER BY b.date DESC, b.start DESC", fetch=True)
    return [(c, r, u, d, s, m, booking_state(d, s, st)) for c, r, u, d, s, m, st in rows]


# ---------------- Resources ----------------
def get_campus_resources(campus_id):
    return run("SELECT id, code, name FROM resources WHERE campus_id=? ORDER BY code",
               (campus_id,), fetch=True)


def get_all_resources():
    return run("SELECT c.name, r.code, r.name FROM resources r "
               "JOIN campuses c ON c.id = r.campus_id ORDER BY c.name, r.code",
               fetch=True)


def resource_status_now(resource_id):
    """'In use' if a booking is happening right now, otherwise 'Available'."""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    now_minutes = now.hour * 60 + now.minute
    rows = run("SELECT start, duration FROM bookings "
               "WHERE resource_id=? AND date=? AND status='Active'",
               (resource_id, today), fetch=True)
    for start, duration in rows:
        if to_minutes(start) <= now_minutes < to_minutes(start) + duration:
            return "In use"
    return "Available"


def add_resource(code, name, campus_id):
    """Add a resource. Returns an error message or None."""
    code = code.strip().upper()
    name = name.strip()
    if not code or not name:
        return "Please enter both a resource code and a resource name."
    try:
        run("INSERT INTO resources (code, name, campus_id) VALUES (?, ?, ?)",
            (code, name, campus_id))
    except sqlite3.IntegrityError:
        return "A resource with that code already exists."
    return None


def update_resource(resource_id, code, name):
    """Change a resource. Returns an error message or None."""
    code = code.strip().upper()
    name = name.strip()
    if not code or not name:
        return "Please enter both a resource code and a resource name."
    try:
        run("UPDATE resources SET code=?, name=? WHERE id=?", (code, name, resource_id))
    except sqlite3.IntegrityError:
        return "Another resource already uses that code."
    return None


def remove_resource(resource_id):
    run("DELETE FROM bookings WHERE resource_id=?", (resource_id,))
    run("DELETE FROM resources WHERE id=?", (resource_id,))


# ---------------- Reports ----------------
def campus_report(campus_id):
    """Returns (total bookings, average minutes, list of (resource, bookings))."""
    total = run("SELECT COUNT(*) FROM bookings WHERE campus_id=? AND status='Active'",
                (campus_id,), fetch=True)[0][0]
    average = run("SELECT AVG(duration) FROM bookings WHERE campus_id=? AND status='Active'",
                  (campus_id,), fetch=True)[0][0] or 0
    usage = run("SELECT r.name, COUNT(b.id) FROM resources r "
                "LEFT JOIN bookings b ON b.resource_id = r.id AND b.status='Active' "
                "WHERE r.campus_id=? GROUP BY r.id "
                "ORDER BY COUNT(b.id) DESC, r.name", (campus_id,), fetch=True)
    return total, average, usage


def compare_campuses():
    """One row per campus: name, resources, bookings, average, longest, busiest, policy."""
    rows = []
    for campus_id, name in run("SELECT id, name FROM campuses ORDER BY name", fetch=True):
        total, average, usage = campus_report(campus_id)
        longest = run("SELECT MAX(duration) FROM bookings "
                      "WHERE campus_id=? AND status='Active'",
                      (campus_id,), fetch=True)[0][0] or 0
        busiest = usage[0][0] if usage and usage[0][1] > 0 else "-"
        rows.append((name, len(usage), total, round(average), longest,
                     busiest, policy_text(name)))
    return rows
