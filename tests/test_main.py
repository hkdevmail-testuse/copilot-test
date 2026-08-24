import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import CurrentUser, _authorize, _validate_profile_fields, app, get_current_user


def test_profile_page_and_api_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("PROFILE_DB_PATH", str(tmp_path / "profile.db"))
    from app.db import init_db

    init_db()
    headers = {"x-user-id": "user-1", "x-role": "user"}

    with TestClient(app) as client:
        page = client.get("/")
        assert page.status_code == 200

        loaded = client.get("/users/user-1/profile", headers=headers)
        assert loaded.status_code == 200
        assert loaded.json()["profile"]["id"] == "user-1"

        saved = client.put(
            "/users/user-1/profile",
            headers=headers,
            data={
                "first_name": "Ada",
                "last_name": "Lovelace",
                "phone": "12345678",
                "version": "1",
            },
        )
        assert saved.status_code == 200
        assert saved.json()["profile"]["first_name"] == "Ada"



def test_get_current_user_requires_headers_and_normalizes_role():
    current_user = get_current_user(x_user_id="user-1", x_role="Support")

    assert current_user.user_id == "user-1"
    assert current_user.role == "support"

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(x_user_id="user-1")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authentication required"


def test_validate_profile_fields_reports_missing_and_invalid_values():
    errors = _validate_profile_fields("   ", "Lovelace", "abc")

    assert errors["first_name"] == "First name is required"
    assert errors["phone"] == "Phone must contain only digits and be 8-11 characters long"


def test_authorize_allows_admins_and_support_but_blocks_other_users():
    _authorize(CurrentUser("admin", "admin"), "some-user")
    _authorize(CurrentUser("support", "support"), "some-user")

    with pytest.raises(HTTPException) as exc_info:
        _authorize(CurrentUser("user-1", "user"), "user-2")

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Forbidden"
