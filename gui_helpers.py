"""
gui_helpers.py - Small tools shared by all the screens.
"""

import tkinter as tk
from tkinter import ttk

PINK = "#FFC0CB"


class Session:
    """Remembers who is logged in and which campus is active."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.user = None
        self.campus_id = None
        self.campus_name = None


def clear_window(window):
    """Remove everything from the window before showing a new screen."""
    for widget in window.winfo_children():
        widget.destroy()


def make_label(parent, text, size=11, bold=False):
    style = "bold" if bold else "normal"
    return tk.Label(parent, text=text, bg=PINK, font=("Arial", size, style))


def make_table(parent, columns, height=12):
    """columns is a list of (heading, width), e.g. [("Code", 100), ("Name", 200)]."""
    table = ttk.Treeview(parent, columns=[name for name, width in columns],
                         show="headings", height=height)
    for name, width in columns:
        table.heading(name, text=name)
        table.column(name, width=width, anchor="center")
    return table


def fill_table(table, rows):
    """Replace everything in the table with the given rows."""
    for item in table.get_children():
        table.delete(item)
    for row in rows:
        table.insert("", "end", values=row)


def show_header(window, session, title, logout):
    """Title, logged-in user, active campus, booking policy and Logout button."""
    from rules import policy_text
    top = tk.Frame(window, bg=PINK)
    top.pack(fill="x", padx=15, pady=8)
    make_label(top, title, 16, True).pack(side="left")
    tk.Button(top, text="Logout", command=logout).pack(side="right")
    make_label(window, f"Logged in as: {session.user.get_username()} "
                       f"({session.user.role})").pack(anchor="w", padx=15)
    if session.campus_name:
        make_label(window, f"Active campus: {session.campus_name}", 12, True).pack(anchor="w", padx=15)
        make_label(window, "Booking policy: " + policy_text(session.campus_name)).pack(anchor="w", padx=15)
    else:
        make_label(window, "Active campus: All campuses", 12, True).pack(anchor="w", padx=15)

