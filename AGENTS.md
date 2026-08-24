# User Profile Management

FastAPI prototype for updating a registered user's profile (name, phone, avatar).

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:8000 (profile UI) or http://127.0.0.1:8000/docs (OpenAPI).

Local auth is header-based: `x-user-id` and `x-role` (`user`, `admin`, or `support`).

## Test

```powershell
pytest -q
```

## Layout

- `app/main.py` — HTTP API and profile page
- `app/db.py` — SQLite profiles and audit log
- `app/storage.py` — local avatar files under `static/`
- `app/config.py` — `PROFILE_DB_PATH`, `PROFILE_STORAGE_ROOT`, `PROFILE_STATIC_ROOT`
- `.cursor/agents/` — project subagents (converted from GitHub Copilot agents)
- `.cursor/rules/` — coding conventions

## Conventions

- Do not invent requirements. User stories live in `User_Story_User_Profile_Management.txt`.
- Profile updates use optimistic locking (`version`); stale updates return `409`.
- Email is not editable.
- Phone is digits only, 8–11 characters, unique across users.
- Images: JPEG/PNG/WebP, max 5MB, processed to 1024px and 128px JPEGs.
