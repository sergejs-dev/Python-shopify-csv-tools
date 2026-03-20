
import os
import hashlib
import ctypes
from datetime import datetime
import sys

def resource_path(relative_path):
    try:
        base_path =sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path,relative_path)     

# 🔐 секрет (тот же, что в генераторе)
SECRET_KEY = "moon_secret_2026"

# 📁 системная папка
BASE_DIR = os.path.join(os.getenv("LOCALAPPDATA"), "MoonShopifyTool")
os.makedirs(BASE_DIR, exist_ok=True)

LICENSE_FILE =os.path.join(BASE_DIR, "sys.dat")
DEMO_FILE = os.path.join(BASE_DIR, "cache.dat")

# =========================
# 🔐 LICENSE LOGIC
# =========================

def generate_license(machine_id: str) -> str:
    raw = machine_id + SECRET_KEY
    return hashlib.sha256(raw.encode()).hexdigest()[:20].upper()


def validate_license(machine_id: str, key: str) -> bool:
    return generate_license(machine_id) == key


def is_licensed() -> bool:
    if not os.path.exists(LICENSE_FILE):
        return False

    try:
        with open(LICENSE_FILE, "r") as f:
            key = f.read().strip()

        import uuid
        machine_id = str(uuid.getnode())

        return validate_license(machine_id, key)

    except:
        return False


# =========================
# ⏳ DEMO LOGIC
# =========================

def hide_file(path):
    try:
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN)
    except:
        pass


def save_demo_start():
    if not os.path.exists(DEMO_FILE):
        os.makedirs(BASE_DIR, exist_ok=True)

        now = datetime.now().isoformat()
        with open(DEMO_FILE, "w") as f:
            f.write(now)

        hide_file(DEMO_FILE)


def load_demo_start():
    if not os.path.exists(DEMO_FILE):
        return None

    with open(DEMO_FILE, "r") as f:
        return f.read().strip()


def check_demo_days():
    start_str = load_demo_start()

    if not start_str:
        save_demo_start()
        return 14

    try:
        start_date = datetime.fromisoformat(start_str)
    except:
        return 0

    now = datetime.now()
    days_used = (now - start_date).days
    remaining = 14 - days_used

    return max(0, remaining) 