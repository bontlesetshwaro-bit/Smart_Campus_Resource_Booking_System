"""
lecturer_screen.py - Campus selection, booking and booking history for lecturers.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from gui_helpers import PINK, clear_window, make_label, make_table, fill_table, show_header
from database import run
from rules import policy_text, open_dates, time_options, duration_options
from booking import (get_campus_resources, is_available, create_booking,
                     get_user_bookings, cancel_booking)


def show_lecturer(window, session, logout):
    """Lecturers must choose a campus first."""
    if session.campus_name is None:
        show_campus_choice(window, session, logout)
    else:
        show_booking_screen(window, session, logout)


def show_campus_choice(window, session, logout):
    clear_window(window)
    box = tk.Frame(window, bg=PINK)
    box.pack(expand=True)
    make_label(box, "Select a Campus", 18, True).pack(pady=10)

    campuses = run("SELECT id, name FROM campuses ORDER BY name", fetch=True)
    campus_box = ttk.Combobox(box, values=[name for campus_id, name in campuses],
                              state="readonly", width=25)
    campus_box.current(0)
    campus_box.pack(pady=5)
    policy_label = make_label(box, "")
    policy_label.pack(pady=5)

    def show_policy(event=None):
        policy_label.config(text="Booking policy: " + policy_text(campus_box.get()))

    campus_box.bind("<<ComboboxSelected>>", show_policy)
    show_policy()

    def continue_clicked():
        for campus_id, name in campuses:
            if name == campus_box.get():
                session.campus_id = campus_id
                session.campus_name = name
        show_booking_screen(window, session, logout)

    tk.Button(box, text="Continue", width=15, command=continue_clicked).pack(pady=8)
    tk.Button(box, text="Logout", width=15, command=logout).pack()


def show_booking_screen(window, session, logout):
    clear_window(window)
    show_header(window, session, "Lecturer", logout)

    def change_campus():
        session.campus_id = None
        session.campus_name = None
        show_campus_choice(window, session, logout)

    tk.Button(window, text="Change campus", command=change_campus).pack(anchor="w", padx=15)

    tabs = ttk.Notebook(window)
    tabs.pack(fill="both", expand=True, padx=15, pady=10)
    book_tab = tk.Frame(tabs, bg=PINK)
    my_tab = tk.Frame(tabs, bg=PINK)
    tabs.add(book_tab, text="Book a Resource")
    tabs.add(my_tab, text="My Bookings")

    # ---------- Tab 1: book a resource ----------
    make_label(book_tab, "1. Choose the date, start time and duration.   "
                         "2. Select a resource.   3. Click Book.").pack(anchor="w", padx=10, pady=8)
    choices = tk.Frame(book_tab, bg=PINK)
    choices.pack(anchor="w", padx=10)

    make_label(choices, "Date").grid(row=0, column=0, padx=5)
    date_box = ttk.Combobox(choices, values=open_dates(session.campus_name),
                            state="readonly", width=22)
    date_box.current(0)
    date_box.grid(row=1, column=0, padx=5)

    make_label(choices, "Start time").grid(row=0, column=1, padx=5)
    times = time_options(session.campus_name)
    time_box = ttk.Combobox(choices, values=times, state="readonly", width=10)
    time_box.current(times.index("09:00") if "09:00" in times else 0)
    time_box.grid(row=1, column=1, padx=5)

    make_label(choices, "Duration (minutes)").grid(row=0, column=2, padx=5)
    durations = [str(d) for d in duration_options(session.campus_name)]
    duration_box = ttk.Combobox(choices, values=durations, state="readonly", width=10)
    duration_box.current(durations.index("60") if "60" in durations else 0)
    duration_box.grid(row=1, column=2, padx=5)

    resource_table = make_table(book_tab, [("Code", 120), ("Resource", 220),
                                           ("Status for chosen time", 200)], height=8)
    resource_table.pack(anchor="w", padx=10, pady=10)

    def chosen_time():
        return date_box.get()[:10], time_box.get(), int(duration_box.get())

    def refresh_resources(event=None):
        date, start, duration = chosen_time()
        for item in resource_table.get_children():
            resource_table.delete(item)
        for resource_id, code, name in get_campus_resources(session.campus_id):
            if is_available(resource_id, date, start, duration):
                status = "Available"
            else:
                status = "Already booked"
            resource_table.insert("", "end", iid=str(resource_id), values=(code, name, status))

    for box in (date_box, time_box, duration_box):
        box.bind("<<ComboboxSelected>>", refresh_resources)

    def book_clicked():
        selected = resource_table.selection()
        if not selected:
            messagebox.showwarning("No resource", "Please select a resource in the table first.")
            return
        date, start, duration = chosen_time()
        resource_name = resource_table.item(selected[0])["values"][1]
        question = f"Book {resource_name} on {date} at {start} for {duration} minutes?"
        if not messagebox.askyesno("Confirm booking", question):
            return
        error = create_booking(session.user.get_id(), session.campus_id, session.campus_name,
                               int(selected[0]), date, start, duration)
        if error:
            messagebox.showerror("Booking not allowed", error)
        else:
            messagebox.showinfo("Booked", "Your booking has been saved.")
        refresh_resources()
        refresh_my_bookings()

    tk.Button(book_tab, text="Book selected resource", command=book_clicked).pack(anchor="w", padx=10)

    # ---------- Tab 2: my bookings ----------
    top = tk.Frame(my_tab, bg=PINK)
    top.pack(anchor="w", padx=10, pady=8)
    make_label(top, "Show:").pack(side="left")
    filter_box = ttk.Combobox(top, values=["All", "Upcoming", "Past", "Cancelled"],
                              state="readonly", width=12)
    filter_box.current(0)
    filter_box.pack(side="left", padx=5)

    my_table = make_table(my_tab, [("Campus", 100), ("Resource", 160), ("Date", 100),
                                   ("Start", 70), ("Minutes", 70), ("Status", 100)], height=10)
    my_table.pack(anchor="w", padx=10)

    def refresh_my_bookings(event=None):
        for item in my_table.get_children():
            my_table.delete(item)
        for booking_id, campus, resource, date, start, minutes, state in \
                get_user_bookings(session.user.get_id(), filter_box.get()):
            my_table.insert("", "end", iid=str(booking_id),
                            values=(campus, resource, date, start, minutes, state))

    filter_box.bind("<<ComboboxSelected>>", refresh_my_bookings)

    def cancel_clicked():
        selected = my_table.selection()
        if not selected:
            messagebox.showwarning("No booking", "Please select a booking to cancel.")
            return
        if not messagebox.askyesno("Cancel booking", "Do you really want to cancel this booking?"):
            return
        error = cancel_booking(int(selected[0]))
        if error:
            messagebox.showerror("Cannot cancel", error)
        else:
            messagebox.showinfo("Cancelled", "The booking was cancelled.")
        refresh_my_bookings()
        refresh_resources()

    tk.Button(my_tab, text="Cancel selected booking", command=cancel_clicked).pack(anchor="w", padx=10, pady=8)

    refresh_resources()
    refresh_my_bookings()
