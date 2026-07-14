import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def get_db_path() -> Path:
    return Path(os.getenv("PROFILE_DB_PATH", str(BASE_DIR / "profile.db"))).resolve()


def get_storage_root() -> Path:
    return Path(os.getenv("PROFILE_STORAGE_ROOT", str(BASE_DIR / "storage"))).resolve()


def get_static_root() -> Path:
    return Path(os.getenv("PROFILE_STATIC_ROOT", str(BASE_DIR / "static"))).resolve()
