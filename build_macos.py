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
# PyInstaller creates dist/EmployeeDatabase.app for --windowed on macOS.
if not APP_BUNDLE.exists():
    raise RuntimeError("Expected app bundle was not created at dist/EmployeeDatabase.app")

# Ensure Frameworks dir exists and locate the Python runtime produced by PyInstaller.
frameworks_dir = APP_BUNDLE / "Contents" / "Frameworks"
frameworks_dir.mkdir(parents=True, exist_ok=True)

# Known candidate names PyInstaller may use
candidates = [
    "python3__dot__11",
    "python3.11",
    "libpython3.11.dylib",
    "python3.11.dylib",
    "python3.11"
]
source = None
for name in candidates:
    p = frameworks_dir / name
    if p.exists():
        source = p
        break

# Fallback: search for any file with 'python' in the name inside Frameworks
if source is None:
    for p in frameworks_dir.glob("**/*python*"):
        if p.is_file():
            source = p
            break

if source is not None:
    dest = frameworks_dir / "python3.11"
    # If the canonical python3.11 file is missing, copy the found runtime into place
    if not dest.exists():
        try:
            shutil.copy2(source, dest)
            dest.chmod(0o755)
        except Exception:
            # best-effort; ignore failures here and continue to create symlink
            pass

# Create the internal loader path expected by some PyInstaller bundles
macos_dir = APP_BUNDLE / "Contents" / "MacOS"
internal_dir = macos_dir / "_internal"
internal_dir.mkdir(parents=True, exist_ok=True)
internal_python = internal_dir / "Python"
internal_target = Path("../Frameworks/python3.11")
if not internal_python.exists():
    try:
        internal_python.symlink_to(internal_target)
    except Exception:
        # On some environments symlinks may fail; fallback to copying if source exists
        if (frameworks_dir / "python3.11").exists():
            try:
                shutil.copy2(frameworks_dir / "python3.11", internal_python)
            except Exception:
                pass

print(f"Built app bundle at {APP_BUNDLE}")
