"""
admin_screen.py - Screen for the campus administrator.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from gui_helpers import PINK, clear_window, make_label, make_table, fill_table, show_header
from booking import (get_campus_resources, resource_status_now, add_resource,
                     update_resource, remove_resource, get_campus_bookings, campus_report)


def show_admin(window, session, logout):
    clear_window(window)
    show_header(window, session, "Campus Administrator", logout)

    tabs = ttk.Notebook(window)
    tabs.pack(fill="both", expand=True, padx=15, pady=10)
    resource_tab = tk.Frame(tabs, bg=PINK)
    booking_tab = tk.Frame(tabs, bg=PINK)
    report_tab = tk.Frame(tabs, bg=PINK)
    tabs.add(resource_tab, text="Resources")
    tabs.add(booking_tab, text="Campus Bookings")
    tabs.add(report_tab, text="Campus Report")

    # ---------- Tab 1: resources ----------
    resource_table = make_table(resource_tab, [("Code", 120), ("Resource", 220),
                                               ("Right now", 110)], height=12)
    resource_table.pack(side="left", anchor="n", padx=10, pady=10)

    form = tk.Frame(resource_tab, bg=PINK)
    form.pack(side="left", anchor="n", padx=20, pady=10)
    make_label(form, "Resource code (must be unique)").pack(anchor="w")
    code_entry = tk.Entry(form, width=28)
    code_entry.pack(pady=3)
    make_label(form, "Resource name").pack(anchor="w")
    name_entry = tk.Entry(form, width=28)
    name_entry.pack(pady=3)
    make_label(form, "Tip: click a resource in the table\nto edit or remove it.").pack(anchor="w", pady=5)

    def refresh_resources():
        for item in resource_table.get_children():
            resource_table.delete(item)
        for resource_id, code, name in get_campus_resources(session.campus_id):
            resource_table.insert("", "end", iid=str(resource_id),
                                  values=(code, name, resource_status_now(resource_id)))

    def table_clicked(event=None):
        selected = resource_table.selection()
        if selected:
            values = resource_table.item(selected[0])["values"]
            code_entry.delete(0, "end")
            code_entry.insert(0, str(values[0]))
            name_entry.delete(0, "end")
            name_entry.insert(0, str(values[1]))

    resource_table.bind("<<TreeviewSelect>>", table_clicked)

    def clear_form():
        code_entry.delete(0, "end")
        name_entry.delete(0, "end")

    def add_clicked():
        error = add_resource(code_entry.get(), name_entry.get(), session.campus_id)
        if error:
            messagebox.showerror("Cannot add", error)
        else:
            messagebox.showinfo("Added", "The resource was added.")
            clear_form()
            refresh_resources()

    def update_clicked():
        selected = resource_table.selection()
        if not selected:
            messagebox.showwarning("No resource", "Please click a resource in the table first.")
            return
        error = update_resource(int(selected[0]), code_entry.get(), name_entry.get())
        if error:
            messagebox.showerror("Cannot update", error)
        else:
            messagebox.showinfo("Updated", "The resource was updated.")
            clear_form()
            refresh_resources()

    def remove_clicked():
        selected = resource_table.selection()
        if not selected:
            messagebox.showwarning("No resource", "Please click a resource in the table first.")
            return
        if messagebox.askyesno("Remove", "Remove this resource and all of its bookings?"):
            remove_resource(int(selected[0]))
            clear_form()
            refresh_resources()

    tk.Button(form, text="Add resource", width=18, command=add_clicked).pack(pady=3)
    tk.Button(form, text="Update selected", width=18, command=update_clicked).pack(pady=3)
    tk.Button(form, text="Remove selected", width=18, command=remove_clicked).pack(pady=3)

    # ---------- Tab 2: bookings of this campus ----------
    booking_table = make_table(booking_tab, [("Resource", 150), ("Lecturer", 130), ("Date", 100),
                                             ("Start", 70), ("Minutes", 70), ("Status", 100)], height=14)
    booking_table.pack(anchor="w", padx=10, pady=10)

    # ---------- Tab 3: report ----------
    report_label = tk.Label(report_tab, bg=PINK, font=("Arial", 12), justify="left")
    report_label.pack(anchor="w", padx=20, pady=20)

    def build_report():
        total, average, usage = campus_report(session.campus_id)
        text = f"Campus: {session.campus_name}\n\n"
        text += f"Total number of bookings: {total}\n"
        text += f"Average booking duration: {average:.0f} minutes\n\n"
        text += "Most frequently used resources:\n"
        busy = [(name, count) for name, count in usage if count > 0][:3]
        if busy:
            for number, (name, count) in enumerate(busy, 1):
                text += f"   {number}. {name} - {count} bookings\n"
        else:
            text += "   No bookings yet\n"
        text += "\nUsage of every resource:\n"
        for name, count in usage:
            text += f"   {name}: {count} bookings\n"
        report_label.config(text=text)

    def refresh_all(event=None):
        refresh_resources()
        fill_table(booking_table, get_campus_bookings(session.campus_id))
        build_report()

    tabs.bind("<<NotebookTabChanged>>", refresh_all)
    refresh_all()

