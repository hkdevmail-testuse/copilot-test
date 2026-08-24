from app.db import ensure_user, get_connection, get_profile, init_db, phone_exists, update_profile


def test_init_db_and_profile_update_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("PROFILE_DB_PATH", str(tmp_path / "profile.db"))

    init_db()

    with get_connection() as conn:
        profile = ensure_user(conn, "user-123")
        assert profile["id"] == "user-123"
        assert profile["email"] == "user-123@example.com"
        assert profile["first_name"] == ""
        assert profile["version"] == 1

        updated_profile, changes = update_profile(
            conn=conn,
            user_id="user-123",
            first_name="Ada",
            last_name="Lovelace",
            phone="12345678",
            avatar_key=None,
            thumbnail_key=None,
            avatar_url="/static/user-123/avatar-1024.jpg",
            provided_version=1,
            actor_id="admin",
        )

        assert updated_profile["first_name"] == "Ada"
        assert updated_profile["last_name"] == "Lovelace"
        assert updated_profile["phone"] == "12345678"
        assert updated_profile["version"] == 2
        assert changes["first_name"] == "Ada"
        assert changes["last_name"] == "Lovelace"
        assert changes["phone"] == "12345678"

        assert get_profile(conn, "user-123")["version"] == 2
        assert phone_exists(conn, "12345678", "another-user") is True


def test_phone_conflict_detection_is_user_specific(tmp_path, monkeypatch):
    monkeypatch.setenv("PROFILE_DB_PATH", str(tmp_path / "profile.db"))

    init_db()

    with get_connection() as conn:
        ensure_user(conn, "user-1")
        ensure_user(conn, "user-2")
        update_profile(
            conn=conn,
            user_id="user-1",
            first_name="Alice",
            last_name="Smith",
            phone="55512345",
            avatar_key=None,
            thumbnail_key=None,
            avatar_url=None,
            provided_version=1,
            actor_id="admin",
        )

        assert phone_exists(conn, "55512345", "user-1") is False
        assert phone_exists(conn, "55512345", "user-2") is True
