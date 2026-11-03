"""
login_screen.py - Login and register screens.
"""

import sqlite3
import tkinter as tk
from tkinter import messagebox
from gui_helpers import PINK, clear_window, make_label
from database import run, hash_password
from user_models import make_user
from lecturer_screen import show_lecturer
from admin_screen import show_admin
from operator_screen import show_operator


def show_login(window, session):
    session.reset()
    clear_window(window)
    box = tk.Frame(window, bg=PINK)
    box.pack(expand=True)

    make_label(box, "Smart Campus Resource Booking System", 18, True).pack(pady=10)
    make_label(box, "Username").pack()
    username_entry = tk.Entry(box, width=30)
    username_entry.pack(pady=3)
    make_label(box, "Password").pack()
    password_entry = tk.Entry(box, width=30, show="*")
    password_entry.pack(pady=3)

    def login_clicked(event=None):
        username = username_entry.get().strip()
        password = password_entry.get()
        if username == "" or password == "":
            messagebox.showerror("Missing details", "Please enter your username and password.")
            return
        rows = run("SELECT id, username, role, campus_id FROM users "
                   "WHERE username=? AND password=?",
                   (username, hash_password(password)), fetch=True)
        if not rows:
            messagebox.showerror("Login failed", "Wrong username or password.")
            return
        session.user = make_user(rows[0])
        go_to_dashboard(window, session)

    password_entry.bind("<Return>", login_clicked)
    tk.Button(box, text="Login", width=20, command=login_clicked).pack(pady=8)
    tk.Button(box, text="Register as a Lecturer", width=20,
              command=lambda: show_register(window, session)).pack()


def go_to_dashboard(window, session):
    """Send the user to the screen that belongs to their role."""
    def logout():
        show_login(window, session)

    if session.user.can_view_all_campuses():            # System Operator
        show_operator(window, session, logout)
    elif session.user.can_manage_resources():           # Campus Administrator
        session.campus_id = session.user.campus_id
        session.campus_name = run("SELECT name FROM campuses WHERE id=?",
                                  (session.campus_id,), fetch=True)[0][0]
        show_admin(window, session, logout)
    else:                                               # Lecturer
        show_lecturer(window, session, logout)


def show_register(window, session):
    clear_window(window)
    box = tk.Frame(window, bg=PINK)
    box.pack(expand=True)

    make_label(box, "Register as a Lecturer", 18, True).pack(pady=10)
    make_label(box, "Username").pack()
    username_entry = tk.Entry(box, width=30)
    username_entry.pack(pady=3)
    make_label(box, "Password (at least 6 characters)").pack()
    password_entry = tk.Entry(box, width=30, show="*")
    password_entry.pack(pady=3)
    make_label(box, "Confirm password").pack()
    confirm_entry = tk.Entry(box, width=30, show="*")
    confirm_entry.pack(pady=3)

    def register_clicked():
        username = username_entry.get().strip()
        password = password_entry.get()
        if username == "":
            messagebox.showerror("Missing details", "Please enter a username.")
        elif len(password) < 6:
            messagebox.showerror("Password too short", "The password must have at least 6 characters.")
        elif password != confirm_entry.get():
            messagebox.showerror("Passwords differ", "The two passwords do not match.")
        else:
            try:
                run("INSERT INTO users (username, password, role) VALUES (?, ?, 'Lecturer')",
                    (username, hash_password(password)))
                messagebox.showinfo("Done", "Your account was created. You can now log in.")
                show_login(window, session)
            except sqlite3.IntegrityError:
                messagebox.showerror("Username taken", "That username is already in use.")

    tk.Button(box, text="Create account", width=20, command=register_clicked).pack(pady=8)
    tk.Button(box, text="Back to login", width=20,
              command=lambda: show_login(window, session)).pack()
