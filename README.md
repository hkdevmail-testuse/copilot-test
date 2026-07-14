# User Profile Management API

This workspace contains a FastAPI-based prototype for the profile management flow described in the approved architecture.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test

```bash
pytest -q
```

## Notes

- Profile updates use optimistic locking with a `version` field and return `409 Conflict` on stale updates.
- Images are processed synchronously and stored locally in the `storage/` directory for this prototype.
- The service uses a simple header-based auth stub for local development.
