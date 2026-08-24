# Pull Request: User profile management API

## Summary
Adds a FastAPI prototype for updating a registered user's profile (name, phone, avatar) with SQLite persistence, optimistic locking, and a local profile page.

## Changes Made
- Profile API and UI in `app/`, started with `python run.py`.
- Tests in `tests/test_main.py` and dependencies in `requirements.txt`.
- Cursor agents/rules, `AGENTS.md`, and `User_Story_User_Profile_Management.txt`.
- Replaced `.github/agents/` Copilot files with `.cursor/agents/`.

## Related Issues
- Not available

## Test Evidence
- Caller confirmed the application works and tests passed.
- Automated command: `pytest -q`.

## Steps to Test
1. `pip install -r requirements.txt`
2. `python run.py`
3. Open http://127.0.0.1:8000 and http://127.0.0.1:8000/docs
4. Use headers `x-user-id` and `x-role` (`user`, `admin`, or `support`)

## Known Limitations
- Auth is a local header stub, not a production identity provider.
- Image processing is synchronous.

## Additional Notes
- Target repository: https://github.com/hkdevmail-testuse/agentic-ai-test
- Base branch: `main`
