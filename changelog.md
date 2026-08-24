# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project is maintained under [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- FastAPI user profile API with SQLite persistence, optimistic locking, and local avatar processing.
- Profile UI at `/`, OpenAPI docs at `/docs`, and `python run.py` entrypoint.
- Pytest coverage for profile page load, field validation, and API round-trip.
- Cursor project agents and rules under `.cursor/`, plus `AGENTS.md` and the user story file.

### Changed
- Avatars are stored under `static/`; email remains read-only on the profile form.
- README documents local setup with `requirements.txt` and header-based auth.

### Removed
- GitHub Copilot agent files under `.github/agents/` (replaced by `.cursor/agents/`).
- Tracked Python bytecode under `app/__pycache__/`.
