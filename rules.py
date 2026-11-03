"""
rules.py - Booking rules for each campus.
To add a new campus, copy one block in CAMPUS_RULES and change the values.
"""

from datetime import datetime, timedelta

# Every campus has its own rules.  (closed_days: 0 = Monday ... 6 = Sunday)
CAMPUS_RULES = {
    "Braynston": {
        "max_minutes": 180,
        "open": "07:00",
        "close": "20:00",
        "closed_days": [],
        "policy": "Max 3 hours per booking | Open 07:00 to 20:00 | Open every day",
    },
    "Centurion": {
        "max_minutes": 120,
        "open": "08:00",
        "close": "17:00",
        "closed_days": [6],
        "policy": "Max 2 hours per booking | Open 08:00 to 17:00 | Closed on Sundays",
    },
    "Pretoria": {
        "max_minutes": 60,
        "open": "09:00",
        "close": "16:00",
        "closed_days": [5, 6],
        "policy": "Max 1 hour per booking | Open 09:00 to 16:00 | Closed on weekends",
    },
}


def policy_text(campus_name):
    """The text shown on screen so the user knows which policy applies."""
    return CAMPUS_RULES[campus_name]["policy"]


def to_minutes(time_text):
    """Change '09:30' into 570 minutes."""
    hours, minutes = time_text.split(":")
    return int(hours) * 60 + int(minutes)


def time_options(campus_name):
    """Start times (every 30 minutes) that the campus allows."""
    rules = CAMPUS_RULES[campus_name]
    options = []
    minutes = to_minutes(rules["open"])
    last_start = to_minutes(rules["close"]) - 30
    while minutes <= last_start:
        options.append(f"{minutes // 60:02d}:{minutes % 60:02d}")
        minutes += 30
    return options


def duration_options(campus_name):
    """Durations (in minutes) up to the campus maximum."""
    return list(range(30, CAMPUS_RULES[campus_name]["max_minutes"] + 1, 30))


def open_dates(campus_name, days=14):
    """The next few days on which the campus accepts bookings."""
    closed = CAMPUS_RULES[campus_name]["closed_days"]
    dates = []
    today = datetime.now().date()
    for i in range(days):
        day = today + timedelta(days=i)
        if day.weekday() not in closed:
            dates.append(day.strftime("%Y-%m-%d (%A)"))
    return dates


def check_booking_rules(campus_name, date_text, start_text, duration):
    """Returns an error message if a rule is broken, otherwise None."""
    rules = CAMPUS_RULES[campus_name]
    if duration > rules["max_minutes"]:
        return f"{campus_name} allows a maximum of {rules['max_minutes']} minutes per booking."
    start = to_minutes(start_text)
    if start < to_minutes(rules["open"]) or start + duration > to_minutes(rules["close"]):
        return f"{campus_name} bookings must be between {rules['open']} and {rules['close']}."
    weekday = datetime.strptime(date_text, "%Y-%m-%d").weekday()
    if weekday in rules["closed_days"]:
        return f"{campus_name} does not take bookings on that day."
