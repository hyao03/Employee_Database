"""
Employee Database GUI

This GUI allows users to manage employee records in a SQLite database.
Users can add, update, delete, and search for employees.
The GUI is built using Tkinter and interacts with the database through the `database.py` module.
"""

import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import database

root = tk.Tk()
root.title("Employee Database")
root.geometry("900x600")

attachment_cache = {}


def get_attachment_paths(attachment_text):
    if not attachment_text:
        return []

    paths = []
    for line in str(attachment_text).splitlines():
        path = line.strip()
        if path:
            paths.append(path)
    return paths


def format_attachment_display(attachment_text):
    return "Attachments"


def open_attachment_path(path):
    if not path:
        return False

    if os.path.exists(path):
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", path])
            elif os.name == "nt":
                os.startfile(path)
            else:
                subprocess.Popen(["xdg-open", path])
            return True
        except OSError:
            return False

    return False


def clear_entries():
    first_name_entry.delete(0, tk.END)
    last_name_entry.delete(0, tk.END)
    dob_entry.delete(0, tk.END)
    ssn_entry.delete(0, tk.END)
    employment_date_entry.delete(0, tk.END)
    termination_date_entry.delete(0, tk.END)
    pay_rate_entry.delete(0, tk.END)
    status_entry.delete(0, tk.END)
    attachments_text.delete(1.0, tk.END)

# Save employee data to the database
def save_employee():
    # Collect and trim inputs
    first = first_name_entry.get().strip()
    last = last_name_entry.get().strip()
    dob = dob_entry.get().strip()
    ssn = ssn_entry.get().strip()
    employment_date = employment_date_entry.get().strip()
    termination_date = termination_date_entry.get().strip() or None
    pay_rate_str = pay_rate_entry.get().strip()
    status = status_entry.get().strip()
    attachments = attachments_text.get("1.0", tk.END).strip() or None

    # Check required fields
    required = {
        "First Name": first,
        "Last Name": last,
        "Date of Birth": dob,
        "SSN": ssn,
        "Employment Date": employment_date,
        "Status": status,
        "Pay Rate": pay_rate_str,
    }
    missing = [name for name, val in required.items() if not val]
    if missing:
        messagebox.showerror("Missing fields", "Please fill out: " + ", ".join(missing))
        return

    # Validate SSN format and pay rate value
    if not database.validate_ssn(ssn):
        messagebox.showerror("Invalid SSN", "SSN must be 9 digits (numbers only).")
        return

    # Use database-level validation to avoid duplicating logic
    if not database.validate_pay_rate(pay_rate_str):
        messagebox.showerror("Invalid Pay Rate", "Pay rate must be a non-negative number.")
        return
    pay_rate = float(pay_rate_str)

    try:
        database.add_employee(
            first,
            last,
            dob,
            ssn,
            employment_date,
            termination_date,
            pay_rate,
            status,
            attachments,
        )
        load_data()
        clear_entries()

        messagebox.showinfo(
            "Success",
            "Employee added"
        )
    except ValueError as e:
        messagebox.showerror(
            "Invalid input",
            str(e)
        )

# Load employee data into entry fields when a row is selected
def load_selected_employee(event):
    selected = tree.focus()
    if not selected:
        return

    values = tree.item(selected, "values")
    clear_entries()

    first_name_entry.insert(0, values[0])
    last_name_entry.insert(0, values[1])
    dob_entry.insert(0, values[2])
    ssn_entry.insert(0, values[3])
    employment_date_entry.insert(0, values[4])
    termination_date_entry.insert(0, values[5])
    pay_rate_entry.insert(0, values[6])
    status_entry.insert(0, values[7])
    raw_attachments = attachment_cache.get(str(selected), values[8])
    attachments_text.insert(1.0, raw_attachments or "")

# Update employee data in the database
def update_employee():
    selected = tree.focus()
    if not selected:
        messagebox.showerror(
            "Error",
            "Please select an employee first."
        )
        return

    # Check and trim inputs
    db_id = int(selected)
    first = first_name_entry.get().strip()
    last = last_name_entry.get().strip()
    dob = dob_entry.get().strip()
    ssn = ssn_entry.get().strip()
    employment_date = employment_date_entry.get().strip()
    termination_date = termination_date_entry.get().strip() or None
    pay_rate_str = pay_rate_entry.get().strip()
    status = status_entry.get().strip()
    attachments = attachments_text.get("1.0", tk.END).strip() or None

    # Required fields validation
    required = {
        "First Name": first,
        "Last Name": last,
        "Date of Birth": dob,
        "SSN": ssn,
        "Employment Date": employment_date,
        "Pay Rate": pay_rate_str,
        "Status": status,
    }
    missing = [name for name, val in required.items() if not val]
    if missing:
        messagebox.showerror("Missing fields", "Please fill out: " + ", ".join(missing))
        return

    # Validate SSN and pay rate using database helpers
    if not database.validate_ssn(ssn):
        messagebox.showerror("Invalid SSN", "SSN must be 9 digits (numbers only).")
        return

    if pay_rate_str and not database.validate_pay_rate(pay_rate_str):
        messagebox.showerror("Invalid Pay Rate", "Pay rate must be a non-negative number.")
        return

    pay_rate = float(pay_rate_str)

    try:
        database.update_employee(
            db_id,
            first,
            last,
            dob,
            ssn,
            employment_date,
            termination_date,
            pay_rate,
            status,
            attachments
        )
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    load_data()
    clear_entries()
    messagebox.showinfo(
        "Success",
        "Employee updated."
    )

# Delete employee from the database
def delete_employee():
    selected = tree.focus()
    if not selected:
        messagebox.showerror(
            "Error",
            "Please select an employee first."
        )
        return

    db_id = int(selected)

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this employee?"
    )

    if confirm:
        database.delete_employee(db_id)
        load_data()
        messagebox.showinfo(
            "Success",
            "Employee deleted."
        )
        clear_entries()

# Top frame
top_frame = tk.Frame(root, padx=10, pady=10)
top_frame.pack(fill="x", padx=10)
top_frame.columnconfigure(0, weight=1)
top_frame.columnconfigure(1, weight=1)

# Frame for employee entry fields
form_frame = tk.Frame(top_frame, padx=10, pady=10)
form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# Frame for search controls
search_frame = tk.Frame(top_frame, padx=10, pady=10)
search_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

# Frame for the employee table
table_frame = tk.Frame(root, padx=10, pady=10)
table_frame.pack(fill="both", expand=True)

# Employee Entry Form

tk.Label(form_frame, text="Employee Entry Form", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=4, pady=10)
tk.Label(form_frame, text="First Name").grid(row=1, column=0, sticky="w", padx=5, pady=3)
first_name_entry = tk.Entry(form_frame)
first_name_entry.grid(row=1, column=1, padx=5, pady=3)

tk.Label(form_frame, text="Last Name").grid(row=1, column=2, sticky="w", padx=5, pady=3)
last_name_entry = tk.Entry(form_frame)
last_name_entry.grid(row=1, column=3, padx=5, pady=3)

tk.Label(form_frame, text="Date of Birth").grid(row=3, column=0, sticky="w", padx=5, pady=3)
dob_entry = tk.Entry(form_frame)
dob_entry.grid(row=3, column=1, padx=5, pady=3)

tk.Label(form_frame, text="SSN").grid(row=3, column=2, sticky="w", padx=5, pady=3)
ssn_entry = tk.Entry(form_frame)
ssn_entry.grid(row=3, column=3, padx=5, pady=3)

tk.Label(form_frame, text="Employment Date").grid(row=5, column=0, sticky="w", padx=5, pady=3)
employment_date_entry = tk.Entry(form_frame)
employment_date_entry.grid(row=5, column=1, padx=5, pady=3)

tk.Label(form_frame, text="Termination Date").grid(row=5, column=2, sticky="w", padx=5, pady=3)
termination_date_entry = tk.Entry(form_frame)
termination_date_entry.grid(row=5, column=3, padx=5, pady=3)

tk.Label(form_frame, text="Pay Rate").grid(row=7, column=0, sticky="w", padx=5, pady=3)
pay_rate_entry = tk.Entry(form_frame)
pay_rate_entry.grid(row=7, column=1, padx=5, pady=3)

tk.Label(form_frame, text="Status").grid(row=8, column=0, sticky="w", padx=5, pady=3)
status_entry = tk.Entry(form_frame)
status_entry.grid(row=8, column=1, padx=5, pady=3)

#tk.Label(form_frame, text="PDF File Path").grid(row=9, column=0, sticky="w", padx=5, pady=3)
#pdf_filepath_entry = tk.Entry(form_frame)
#pdf_filepath_entry.grid(row=9, column=1, padx=5, pady=3)
tk.Label(form_frame, text="Attachments (one per line)").grid(row=9, column=0, sticky="nw", padx=5, pady=3)
attachments_text = tk.Text(form_frame, height=4, width=40)
attachments_text.grid(row=9, column=1, columnspan=3, padx=5, pady=3, sticky="ew")

# Clear Entries button
clear_button = tk.Button(form_frame, text="Clear Form", command=clear_entries)
clear_button.grid(row=11, column=0, columnspan=3, pady=5)

# Add Employee button
add_button = tk.Button(form_frame, text="Add Employee", command=save_employee)
add_button.grid(row=12, column=0, columnspan=1, pady=10)

# Delete Employee button
delete_button = tk.Button(form_frame, text="Delete Employee", command=delete_employee)
delete_button.grid(row=12, column=1, columnspan=1, pady=10)

# Update Employee button
update_button = tk.Button(form_frame, text="Update Employee", command=update_employee)
update_button.grid(row=12, column=2, columnspan=1, pady=10)

# Employee Table
def open_attachment_link(event):
    item = tree.identify_row(event.y)
    if not item:
        return

    column = tree.identify_column(event.x)
    if column != "#9":
        return

    attachment_text = attachment_cache.get(str(item), "")
    for path in get_attachment_paths(attachment_text):
        if open_attachment_path(path):
            return

    messagebox.showwarning("Attachment not found", "No valid attachment path was found to open.")


def open_attachment_selector(event):
    item = tree.identify_row(event.y)
    if not item:
        return

    column = tree.identify_column(event.x)
    if column != "#9":
        return

    attachment_text = attachment_cache.get(str(item), "")
    paths = get_attachment_paths(attachment_text)
    if not paths:
        messagebox.showinfo("Attachments", "No attachments available for this employee.")
        return

    if len(paths) == 1:
        open_attachment_path(paths[0])
        return

    picker = tk.Toplevel(root)
    picker.title("Choose attachment")
    picker.geometry("400x250")
    picker.transient(root)
    picker.grab_set()

    tk.Label(picker, text="Select an attachment to open:", anchor="w").pack(fill="x", padx=10, pady=(10, 5))

    listbox = tk.Listbox(picker, height=min(8, len(paths)))
    listbox.pack(fill="both", expand=True, padx=10, pady=5)

    for path in paths:
        display_name = os.path.basename(path) or path
        listbox.insert(tk.END, display_name)

    def open_selected():
        selection = listbox.curselection()
        if not selection:
            picker.destroy()
            return

        chosen_path = paths[selection[0]]
        picker.destroy()
        open_attachment_path(chosen_path)

    tk.Button(picker, text="Open", command=open_selected).pack(pady=10)


def update_attachment_cursor(event):
    row = tree.identify_row(event.y)
    column = tree.identify_column(event.x)
    if row and column == "#9":
        tree.configure(cursor="hand2")
    else:
        tree.configure(cursor="")


def reset_attachment_cursor(event):
    tree.configure(cursor="")


tree = ttk.Treeview(table_frame, columns=("First","Last","DOB","SSN","Employment Date","Termination Date","Pay Rate","Status","Attachments"), show="headings")
tree.bind("<<TreeviewSelect>>", load_selected_employee)
tree.bind("<Button-1>", open_attachment_selector)
tree.bind("<Motion>", update_attachment_cursor)
tree.bind("<Leave>", reset_attachment_cursor)


for col in ("First","Last","DOB", "SSN","Employment Date","Termination Date","Pay Rate","Status","Attachments"):
    tree.heading(col, text=col)

tree.column("First", width=100, anchor="center")
tree.column("Last", width=100, anchor="center")
tree.column("DOB", width=80, anchor="center")
tree.column("SSN", width=80, anchor="center")
tree.column("Employment Date", width=110, anchor="center")
tree.column("Termination Date", width=100, anchor="center")
tree.column("Pay Rate", width=60, anchor="e")
tree.column("Status", width=70, anchor="center")
tree.column("Attachments", width=250, anchor="w")

# Vertical scrollbar for employee table
scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def insert_employee_row(employee):
    row_id = employee[0]
    raw_attachments = employee[9] if len(employee) > 9 else None
    attachment_cache[str(row_id)] = raw_attachments
    values = list(employee[1:9]) + ["Click to open"]
    tree.insert("", tk.END, iid=row_id, values=values)


def load_data():
    tree.delete(*tree.get_children())
    attachment_cache.clear()
    for employee in database.get_all_employees():
        insert_employee_row(employee)

load_data()

# Search Frame
tk.Label(search_frame, text="Search Employees", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=3, pady=10)
tk.Label(search_frame, text="Search by Name").grid(row=1, column=0,sticky="w", padx=5, pady=3)
name_search_entry = tk.Entry(search_frame)
name_search_entry.grid(row=1, column=1, padx=5, pady=3)
tk.Label(search_frame, text="Search by SSN").grid(row=2, column=0, sticky="w", padx=5, pady=3)
ssn_search_entry = tk.Entry(search_frame)
ssn_search_entry.grid(row=2, column=1, padx=5, pady=3)

# Search Employees by Name or SSN
def search_name():
    tree.delete(*tree.get_children())
    attachment_cache.clear()
    results = database.search_by_name(name_search_entry.get())
    for employee in results:
        insert_employee_row(employee)

def search_ssn():
    tree.delete(*tree.get_children())
    attachment_cache.clear()
    result = database.search_employee(ssn_search_entry.get())
    if result:
        insert_employee_row(result)

# Search buttons
tk.Button(search_frame, text="Search", command=search_name).grid(row=1, column=2, padx=5)
tk.Button(search_frame, text="Search", command=search_ssn).grid(row=2, column=2, padx=5)

# Show all employees button
tk.Button(
    search_frame, text="Show All Employees",command=load_data).grid(row=4, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()

