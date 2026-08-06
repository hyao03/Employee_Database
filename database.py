"""
Database functions for terminated employee records

This module provides functions to manage terminated employee records in a SQLite database.
It includes functionality for adding, updating, deleting, and retrieving employee records, as well as searching by name or SSN.
The SSN is encrypted for security purposes using the Fernet symmetric encryption scheme.
"""

import os
import re
import sys
import sqlite3
from pathlib import Path
from cryptography.fernet import Fernet


def resource_path(relative_path: str) -> str:
    """Return an absolute path to a resource, working for dev and PyInstaller.

    When bundled with PyInstaller the files are unpacked to `sys._MEIPASS`;
    otherwise use the module directory.
    """
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, relative_path)


# Determine data directory. When running a frozen bundle we must store
# writable data outside the bundle (for example in the user's home
# directory); when running from source keep the `data/` folder next to
# the module.
if getattr(sys, "frozen", False):
    # Use a per-user application folder on Windows and other OSes.
    DATA_DIR = os.path.join(str(Path.home()), ".employee_database")
else:
    DATA_DIR = resource_path("data")

DATABASE = os.path.join(DATA_DIR, "golden_garden_employee.db")
# Key file; may be written to a user-writable fallback if package dir is read-only
KEY_FILE = resource_path("secret.key")


def set_database(database_key: str):
    """Set the active database to `data/{database_key}.db`.

    Ensures the `data/` directory exists (creates it next to the application
    when running from source, or inside the bundle when running a frozen
    executable).
    """
    global DATABASE, DATA_DIR
    os.makedirs(DATA_DIR, exist_ok=True)
    DATABASE = os.path.join(DATA_DIR, f"{database_key}.db")

# Create or load encryption key
def load_key():
    # Try to load the key from the package resource location first.
    try:
        with open(KEY_FILE, "rb") as file:
            return file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        # Try writing the key next to the application; if that fails (frozen
        # bundles or non-writable install locations) fall back to a file in
        # the user's home directory.
        try:
            with open(KEY_FILE, "wb") as file:
                file.write(key)
            return key
        except OSError:
            fallback = os.path.join(str(Path.home()), ".secret.key")
            with open(fallback, "wb") as file:
                file.write(key)
            return key

cipher = Fernet(load_key())

def encrypt_ssn(ssn):
    return cipher.encrypt(ssn.encode()).decode()

def decrypt_ssn(encrypted_ssn):
    return cipher.decrypt(encrypted_ssn.encode()).decode()

# Connect to or create database
def connect():
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS terminated_employees (
            db_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            ssn_encrypted TEXT NOT NULL UNIQUE,
            employment_date DATE NOT NULL,
            termination_date DATE,
            pay_rate REAL,
            status TEXT NOT NULL,
            attachments TEXT
        )
    """)
    conn.commit()
    return conn

# Validate new employee data before adding to the database
def validate_ssn(ssn):
    pattern = r"^\d{9}$"
    return re.match(pattern, ssn) is not None

def ssn_exists(ssn, exclude_id=None):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT db_id, ssn_encrypted FROM terminated_employees")
    rows = cursor.fetchall()

    conn.close()

    for db_id, ssn_encrypted in rows:
        if exclude_id is not None and db_id == exclude_id:
            continue
        if decrypt_ssn(ssn_encrypted) == ssn:
            return True

    return False

def validate_pay_rate(pay_rate):
    try:
        value = float(pay_rate)
        return value >= 0
    except (ValueError, TypeError):
        return False

def add_employee(first, last, date_of_birth, ssn, employment_date, termination_date,pay_rate, status, attachments):
    
    if not validate_ssn(ssn):
        raise ValueError("Invalid SSN")

    if ssn_exists(ssn):
        raise ValueError("SSN already exists")

    if not validate_pay_rate(pay_rate):
        raise ValueError("Invalid pay rate")

    conn = connect()
    cursor = conn.cursor()
    ssn_encrypted = encrypt_ssn(ssn)
    cursor.execute(
        "INSERT INTO terminated_employees(first_name,last_name,date_of_birth,ssn_encrypted,employment_date,termination_date,pay_rate,status,attachments) VALUES(?,?,?,?,?,?,?,?,?)",
        (first, last, date_of_birth, ssn_encrypted, employment_date, termination_date, pay_rate, status, attachments)
    )

    conn.commit()
    conn.close()

def update_employee(db_id, first, last, date_of_birth, ssn, employment_date, termination_date, pay_rate, status, attachments):
    if not validate_ssn(ssn):
        raise ValueError("Invalid SSN")

    if ssn_exists(ssn, exclude_id=db_id):
        raise ValueError("SSN already exists")

    if pay_rate is not None and not validate_pay_rate(pay_rate):
        raise ValueError("Invalid pay rate")

    conn = connect()
    cursor = conn.cursor()
    ssn_encrypted = encrypt_ssn(ssn)
    cursor.execute(
        """
        UPDATE terminated_employees
        SET first_name = ?,
            last_name = ?,
            date_of_birth = ?,
            ssn_encrypted = ?,
            employment_date = ?,
            termination_date = ?,
            pay_rate = ?,
            status = ?,
            attachments = ?
        WHERE db_id = ?
        """,
        (
            first,
            last,
            date_of_birth,
            ssn_encrypted,
            employment_date,
            termination_date,
            pay_rate,
            status,
            attachments,
            db_id,
        )
    )
    conn.commit()
    conn.close()

def delete_employee(db_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM terminated_employees WHERE db_id = ?", (db_id,))
    conn.commit()
    conn.close()

def get_all_employees():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            db_id,
            first_name,
            last_name,
            date_of_birth,
            ssn_encrypted,
            employment_date,
            termination_date,
            pay_rate,
            status,
            attachments
        FROM terminated_employees
    """)
    rows = cursor.fetchall()
    conn.close()

    employees = []
    for row in rows:
        row = list(row)
        # decrypt the SSN before sending to GUI
        row[4] = decrypt_ssn(row[4])
        employees.append(row)
    return employees

# Search for an employee by name
def search_by_name(name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM terminated_employees
        WHERE first_name LIKE ?
           OR last_name LIKE ?
    """, (f"%{name}%", f"%{name}%"))
    results = cursor.fetchall()
    conn.close()

    decrypted_results = []
    for row in results:
        row = list(row)
        row[4] = decrypt_ssn(row[4])
        decrypted_results.append(row)
    return decrypted_results


# Search for an employee by SSN
def search_employee(ssn):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM terminated_employees
    """)
    results = cursor.fetchall()
    conn.close()

    # Search after decrypting
    for row in results:
        if decrypt_ssn(row[4]) == ssn:
            row = list(row)
            row[4] = decrypt_ssn(row[4])
            return row
    return None