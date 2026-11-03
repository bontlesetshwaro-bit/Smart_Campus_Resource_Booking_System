# Smart Campus Resource Booking System

A Python desktop application for managing campus resources across multiple campuses with role-based access control.

Built with Tkinter and SQLite.

## Features
- Secure login with role-based dashboards: Admin, Operator, Lecturer
- Multi-campus resource booking (Labs, Lecture Halls, Equipment)
- Booking rules engine (`rules.py`) to prevent double-booking
- Admin can manage users and view all bookings
- Operator can manage resources
- SQLite persistence with clean separation of concerns

## Tech Stack
- Python 3.14
- Tkinter + gui_helpers.py for UI
- SQLite3
- Git / GitHub

## How to Run
1. Clone the repository
2. Open folder in PyCharm
3. Run `main.py`: