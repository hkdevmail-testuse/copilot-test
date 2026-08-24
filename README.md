# User Profile Management API

FastAPI prototype for the profile management flow. This is a Cursor project: rules live in `.cursor/rules/`, subagents in `.cursor/agents/`.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Then open:

- http://127.0.0.1:8000 — profile page
- http://127.0.0.1:8000/docs — API docs

In Cursor, use **Run and Debug → Run Profile API**.

Local auth headers: `x-user-id`, `x-role` (`user`, `admin`, `support`).

## Test

```powershell
pytest -q
```

## Notes

- Profile updates use optimistic locking with a `version` field and return `409 Conflict` on stale updates.
- Images are processed synchronously and stored under `static/` for this prototype.
- Email cannot be changed from the profile page.
