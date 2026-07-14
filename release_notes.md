# Release Notes

## Overview
This change adds a root-level `README.md` for the repository and removes the outdated `test_README.md` file. The new documentation clarifies how to run the prototype locally and how to execute tests.

## New Features
- Added `README.md` with project description, local setup, test commands, and prototype notes.

## Improvements
- Replaced legacy documentation with a consolidated root README.
- Clarified repository onboarding and execution instructions.

## Bug Fixes
- None.

## Breaking Changes
- None.

## Known Issues
- `pytest` succeeded, but the existing FastAPI app emits deprecation warnings for `on_event` event handlers. This is a framework lifecycle warning and does not block current test execution.
- The test suite also surfaces a Starlette deprecation warning recommending `httpx2` for `TestClient` usage.
