import tkinter as tk
from database import setup_database
from gui_helpers import Session, PINK
from login_screen import show_login

setup_database()

window = tk.Tk()
window.title("Smart Campus Resource Booking System")
window.geometry("950x620")
window.configure(bg=PINK)

session = Session()
show_login(window, session)
window.mainloop()
