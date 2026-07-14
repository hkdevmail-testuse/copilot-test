# Pull Request: Add project README and remove obsolete documentation

## Summary of Changes
- Added `README.md` at the repository root with project overview, local setup instructions, test instructions, and prototype notes.
- Removed obsolete `test_README.md` from the base branch.
- Verified diff between `origin/main` and `origin/pr/add-readme` shows only the addition of `README.md` and the removal of `test_README.md`.

## Related Issues
- Not available

## Testing Performed
- Executed `pytest -q` from the repository root with `PYTHONPATH=.` to ensure package imports resolved correctly.
- Result: `8 passed`, `0 failed`, `3 warnings`.
- Note: warnings are related to FastAPI `on_event` lifecycle deprecation and do not affect the current test outcomes.

## Additional Notes
- Source branch: `pr/add-readme`
- Target branch: `main`
- No separate regression or functional issue was identified in the current change scope.
