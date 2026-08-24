# Release Notes

## Release Overview
This release delivers a local FastAPI prototype for user profile management: name, phone, and avatar updates with optimistic locking.

## Highlights
- Profile page and REST API with SQLite storage.
- Avatar processing to 1024px and 128px JPEGs.
- Pytest suite for the main profile flows.

## New Features
- GET/PUT user profile endpoints with `version` conflict handling (`409`).
- Header-based local auth (`x-user-id`, `x-role`).
- `python run.py` to start the server on 127.0.0.1:8000.

## Improvements
- Cursor-oriented project layout (`.cursor/agents`, `.cursor/rules`, `AGENTS.md`).

## Bug Fixes
- Not available

## Breaking Changes
- None identified for this prototype.

## Testing
- `pytest -q` (caller reported passing).

## Known Issues
- FastAPI/Starlette may emit lifecycle or TestClient deprecation warnings.

## Deployment Notes
- Install with `pip install -r requirements.txt`.
- Start with `python run.py`. Do not use this header-auth stub in production.
