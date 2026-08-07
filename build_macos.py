import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
APP_NAME = "EmployeeDatabase"
APP_BUNDLE = DIST / f"{APP_NAME}.app"
DATA_DIR = ROOT / "data"


def run(cmd):
    print("$", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(ROOT))


if APP_BUNDLE.exists():
    shutil.rmtree(APP_BUNDLE)

if not (ROOT / "login.py").exists():
    raise FileNotFoundError("login.py not found in project root")

# Ensure the data directory exists for PyInstaller to add.
DATA_DIR.mkdir(parents=True, exist_ok=True)

run([
    sys.executable,
    "-m",
    "PyInstaller",
    "--name",
    APP_NAME,
    "--windowed",
    "--add-data",
    "passwords.json:.",
    "--add-data",
    "data:data",
    "--hidden-import",
    "PIL",
    "login.py",
])

# PyInstaller creates dist/EmployeeDatabase.app for --windowed on macOS.
if not APP_BUNDLE.exists():
    raise RuntimeError("Expected app bundle was not created at dist/EmployeeDatabase.app")

print(f"Built app bundle at {APP_BUNDLE}")
