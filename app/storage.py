import os
from pathlib import Path
from typing import BinaryIO

from app.config import get_storage_root


class LocalObjectStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or get_storage_root()
        self.root.mkdir(parents=True, exist_ok=True)

    def save_processed_images(self, user_id: str, main_image_path: Path, thumb_image_path: Path) -> tuple[str, str]:
        target_dir = self.root / user_id
        target_dir.mkdir(parents=True, exist_ok=True)
        main_target = target_dir / "avatar-1024.jpg"
        thumb_target = target_dir / "avatar-128.jpg"
        main_image_path.replace(main_target)
        thumb_image_path.replace(thumb_target)
        return str(main_target), str(thumb_target)

    def delete_images(self, user_id: str) -> None:
        target_dir = self.root / user_id
        if target_dir.exists():
            for path in target_dir.glob("*"):
                path.unlink()
            target_dir.rmdir()
