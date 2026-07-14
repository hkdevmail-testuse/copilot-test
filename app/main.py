import re
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Annotated

from fastapi import Depends, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
from fastapi import FastAPI

from app.config import get_static_root
from app.db import get_connection, init_db, get_profile, phone_exists, update_profile
from app.storage import LocalObjectStore

app = FastAPI(title="User Profile Management")

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
PHONE_REGEX = re.compile(r"^\d{8,11}$")
DEFAULT_AVATAR_URL = "/static/default-avatar.svg"

store = LocalObjectStore()


class CurrentUser:
    def __init__(self, user_id: str, role: str) -> None:
        self.user_id = user_id
        self.role = role


def get_current_user(
    x_user_id: Annotated[str | None, Header(alias="x-user-id")] = None,
    x_role: Annotated[str | None, Header(alias="x-role")] = None,
) -> CurrentUser:
    if not x_user_id or not x_role:
        raise HTTPException(status_code=401, detail="Authentication required")
    return CurrentUser(user_id=x_user_id, role=x_role.lower())


@app.on_event("startup")
def startup() -> None:
    init_db()


def _build_error_response(errors: dict[str, str], status_code: int = 422) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"errors": errors})


def _validate_profile_fields(first_name: str | None, last_name: str | None, phone: str | None) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not first_name or not first_name.strip():
        errors["first_name"] = "First name is required"
    if not last_name or not last_name.strip():
        errors["last_name"] = "Last name is required"
    if not phone or not phone.strip():
        errors["phone"] = "Phone number is required"
    else:
        if not PHONE_REGEX.fullmatch(phone.strip()):
            errors["phone"] = "Phone must contain only digits and be 8-11 characters long"
    return errors


def _authorize(current_user: CurrentUser, target_user_id: str) -> None:
    if current_user.role in {"admin", "support"}:
        return
    if current_user.user_id != target_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")


def _process_image(image_bytes: bytes, user_id: str) -> tuple[str | None, str | None, str | None]:
    if not image_bytes:
        return None, None, None

    try:
        with Image.open(BytesIO(image_bytes)) as img:
            img.verify()
        with Image.open(BytesIO(image_bytes)) as img:
            converted = img.convert("RGB")
            width, height = converted.size
            crop_size = min(width, height)
            left = (width - crop_size) // 2
            top = (height - crop_size) // 2
            cropped = converted.crop((left, top, left + crop_size, top + crop_size))
            main = cropped.resize((1024, 1024), Image.Resampling.LANCZOS)
            thumb = cropped.resize((128, 128), Image.Resampling.LANCZOS)

            temp_dir = Path(tempfile.gettempdir()) / user_id
            temp_dir.mkdir(parents=True, exist_ok=True)
            main_path = temp_dir / "avatar-1024.jpg"
            thumb_path = temp_dir / "avatar-128.jpg"
            main.save(main_path, format="JPEG", quality=92)
            thumb.save(thumb_path, format="JPEG", quality=85)
            key_main, key_thumb = store.save_processed_images(user_id, main_path, thumb_path)
            return key_main, key_thumb, f"/static/{user_id}/avatar-1024.jpg"
    except (UnidentifiedImageError, OSError):
        raise ValueError("Unsupported or corrupted image")


@app.get("/users/{user_id}/profile")
def get_profile_endpoint(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    _authorize(current_user, user_id)
    with get_connection() as conn:
        profile = get_profile(conn, user_id)
        if profile is None:
            profile = {
                "id": user_id,
                "email": f"{user_id}@example.com",
                "first_name": "",
                "last_name": "",
                "phone": None,
                "avatar_url": DEFAULT_AVATAR_URL,
                "version": 1,
            }
        return {"profile": profile}


@app.put("/users/{user_id}/profile")
async def update_profile_endpoint(
    user_id: str,
    first_name: Annotated[str | None, Form()] = None,
    last_name: Annotated[str | None, Form()] = None,
    phone: Annotated[str | None, Form()] = None,
    version: Annotated[int | None, Form()] = None,
    image: UploadFile | None = File(default=None),
    remove_image: Annotated[str | None, Form()] = None,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, object]:
    _authorize(current_user, user_id)

    errors = _validate_profile_fields(first_name, last_name, phone)
    if errors:
        return _build_error_response(errors)

    normalized_phone = phone.strip() if phone else None
    with get_connection() as conn:
        profile = get_profile(conn, user_id)
        if profile is not None and phone_exists(conn, normalized_phone, user_id):
            return _build_error_response({"phone": "Phone number already exists"})

        avatar_key = None
        thumbnail_key = None
        avatar_url = DEFAULT_AVATAR_URL
        if remove_image:
            avatar_key = None
            thumbnail_key = None
            avatar_url = DEFAULT_AVATAR_URL
        elif image is not None:
            if image.content_type not in ALLOWED_CONTENT_TYPES:
                return _build_error_response({"image": "Unsupported image format"})
            content = await image.read()
            if len(content) > MAX_IMAGE_SIZE_BYTES:
                return _build_error_response({"image": "Image exceeds 5MB limit"})
            try:
                avatar_key, thumbnail_key, avatar_url = _process_image(content, user_id)
            except ValueError as exc:
                return _build_error_response({"image": str(exc)})

        if profile is None:
            profile = {
                "id": user_id,
                "email": f"{user_id}@example.com",
                "first_name": first_name.strip(),
                "last_name": last_name.strip(),
                "phone": normalized_phone,
                "avatar_url": avatar_url,
                "version": 1,
            }

        try:
            updated_profile, _ = update_profile(
                conn=conn,
                user_id=user_id,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                phone=normalized_phone,
                avatar_key=avatar_key,
                thumbnail_key=thumbnail_key,
                avatar_url=avatar_url,
                provided_version=version,
                actor_id=current_user.user_id,
            )
        except ValueError as exc:
            if str(exc) == "stale_version":
                return JSONResponse(status_code=409, content={"error": "stale_version"})
            raise

        return {"profile": updated_profile}
