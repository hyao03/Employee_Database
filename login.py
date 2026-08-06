"""
Employee Database Login

This module provides a login interface for accessing the employee database.
Users can select a database (Golden Garden or Legend of Asia) and enter the corresponding password to gain access.
Users can also change the password for each database.
"""

import base64
import hashlib
import json
import secrets
import tkinter as tk
from pathlib import Path
import sys
from tkinter import messagebox

import database

if getattr(sys, "frozen", False):
    # When bundled, store the password file in the user's home directory.
    PASSWORD_FILE = Path.home() / ".employee_passwords.json"
else:
    PASSWORD_FILE = Path(__file__).with_name("passwords.json")
PASSWORD_STORE = None

DEFAULT_PASSWORDS = {
    "golden_garden_employee": "admin123",
    "legend_of_asia_employee": "password",
}

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    )
    return {
        "salt": base64.b64encode(salt).decode("ascii"),
        "hash": base64.b64encode(derived_key).decode("ascii"),
        "algorithm": "pbkdf2_sha256",
        "iterations": 200_000,
    }


def verify_password(password, record):
    if not isinstance(record, dict):
        return False
    salt = base64.b64decode(record["salt"].encode("ascii"))
    expected = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        int(record.get("iterations", 200_000)),
    )
    return base64.b64decode(record["hash"].encode("ascii")) == expected


def load_password_store(password_file=None):
    global PASSWORD_STORE
    path = Path(password_file or PASSWORD_FILE)
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            data = {}
    else:
        data = {}

    PASSWORD_STORE = data
    return PASSWORD_STORE


def initialize_password_store(password_file=None):
    store = load_password_store(password_file)
    for key, default_password in DEFAULT_PASSWORDS.items():
        if key not in store:
            store[key] = hash_password(default_password)
    save_password_store(store, password_file)
    return store


def save_password_store(store, password_file=None):
    path = Path(password_file or PASSWORD_FILE)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(store, handle, indent=2)
    return store


def set_password(database_key, new_password, password_file=None):
    store = load_password_store(password_file)
    store[database_key] = hash_password(new_password)
    save_password_store(store, password_file)
    return store

def get_password_record(database_key, password_file=None):
    store = initialize_password_store(password_file)
    return store.get(database_key)

def authenticate(database_key, password, password_file=None):
    record = get_password_record(database_key, password_file)
    if not record:
        return False
    return verify_password(password, record)

def open_change_password_window():
    change_window = tk.Toplevel(login_window)
    change_window.title("Change Password")
    change_window.geometry("360x260")

    selected_database = tk.StringVar(value="golden_garden_employee")

    tk.Label(change_window, text="Select database to change password for:").pack(pady=(10, 5))
    tk.Radiobutton(change_window, text="Golden Garden", variable=selected_database, value="golden_garden_employee").pack(anchor="n", padx=20)
    tk.Radiobutton(change_window, text="Legend of Asia", variable=selected_database, value="legend_of_asia_employee").pack(anchor="n", padx=20)

    tk.Label(change_window, text="Current password:").pack(pady=(5, 0))
    current_password_entry = tk.Entry(change_window, show="*")
    current_password_entry.pack()

    tk.Label(change_window, text="New password:").pack(pady=(5, 0))
    new_password_entry = tk.Entry(change_window, show="*")
    new_password_entry.pack()

    tk.Label(change_window, text="Confirm new password:").pack(pady=(5, 0))
    confirm_password_entry = tk.Entry(change_window, show="*")
    confirm_password_entry.pack()

    def save_new_password():
        database_key = selected_database.get()
        current_password = current_password_entry.get()
        new_password = new_password_entry.get()
        confirm_password = confirm_password_entry.get()

        if not current_password or not new_password or not confirm_password:
            messagebox.showerror("Error", "All password fields are required.")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "New passwords do not match.")
            return

        record = get_password_record(database_key)
        if not record or not verify_password(current_password, record):
            messagebox.showerror("Access Denied", "Current password is incorrect.")
            return

        set_password(database_key, new_password)
        messagebox.showinfo("Success", "Password updated successfully.")
        change_window.destroy()

    tk.Button(change_window, text="Save Password", command=save_new_password).pack(pady=5)


def check_password(database_key):
    entered = password_entry.get()
    if authenticate(database_key, entered):
        # use the data/ directory for database files
        database.set_database(database_key)
        login_window.destroy()
        import GUI
    else:
        messagebox.showerror("Access Denied", "Incorrect password")
        password_entry.delete(0, tk.END)


def login():
    selection = database_selection.get()
    if selection == 1:
        check_password("golden_garden_employee")
    elif selection == 2:
        check_password("legend_of_asia_employee")
    else:
        messagebox.showerror("Error", "Please select a database")


login_window = tk.Tk()
login_window.title("Employee Database Login")
login_window.geometry("340x220")

initialize_password_store()

tk.Label(login_window, text="Select database for login:").pack(pady=(10, 5))

database_selection = tk.IntVar(value=0)
tk.Radiobutton(login_window, text="Golden Garden Employee Database", variable=database_selection, value=1).pack(anchor="n", padx=20)
tk.Radiobutton(login_window, text="Legend of Asia Employee Database", variable=database_selection, value=2).pack(anchor="n", padx=20)

tk.Label(login_window, text="Password:").pack(pady=(10, 0))
password_entry = tk.Entry(login_window, show="*")
password_entry.pack(pady=5)

button_frame = tk.Frame(login_window)
button_frame.pack(pady=8)
tk.Button(button_frame, text="Login", command=login).pack(side="left", padx=5)
tk.Button(button_frame, text="Change Password", command=open_change_password_window).pack(side="left", padx=5)

login_window.mainloop()