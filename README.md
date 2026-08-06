# Terminated Employee Database

A Python desktop application for securely managing records of terminated employees. The application provides an easy-to-use graphical interface for storing, searching, updating, and reviewing employee termination records using an SQLite database.

---

## Features

- Add terminated employee records
- Update existing records
- Delete records
- Search employees by:
  - Name
  - SSN
- View all employee records
- User login and authentication
- Store data in a local database
- User-friendly desktop interface
- Data validation to reduce input errors

---

## Technologies Used

- Python 3.x
- Tkinter (or CustomTkinter/PyQt)
- SQLite
- sqlite3
- PyInstaller (for executable packaging)

---

## Screenshots

### Main Dashboard

(Add screenshot here)

### Employee Search

(Add screenshot here)

### Add Employee Form

(Add screenshot here)

---

## Database

The application uses SQLite as its local database.

Example fields:

- Employee ID
- First Name
- Last Name
- SSN
- DOB
- Start Date
- Termination Date
- Pay Rate
- Status
- Attachments


---

## Windows Packaging

To build the Windows executable:

```bash
pyinstaller --onefile --windowed login.py
```

The executable will be generated inside the `dist` folder.

### macOS packaging (not tested yet)

On a Mac, install PyInstaller and build a `.app` bundle:

```bash
python3 -m pip install pyinstaller
python3 build_macos.py
```

The app bundle will be created at `dist/EmployeeDatabase.app`.

To open it from Terminal:

```bash
open dist/EmployeeDatabase.app
```

If macOS blocks the app, you can clear the quarantine flag:

```bash
xattr -dr com.apple.quarantine dist/EmployeeDatabase.app
```

---

## Project Structure

```
terminated-employee-database/
│
├── assets/
├── data/
│   └── employees.db
├── main.py
├── database.py
├── gui.py
├── requirements.txt
└── README.md
```

---

## Future Improvements

- MacOS Support
- Employee photo support
- PDF report generation
- CSV import/export
- Backup and restore database
- Audit logging
- Role-based permissions

---

## Skills Demonstrated

- Python programming
- GUI development
- Database design
- CRUD operations
- SQL queries
- Object-oriented programming
- Input validation
- Desktop application deployment

---

## License

This project is intended for educational and portfolio purposes.