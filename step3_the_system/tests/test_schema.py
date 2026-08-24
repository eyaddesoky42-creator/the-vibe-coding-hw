import sqlite3

import pytest

from app import db


def test_schema_creates_appointments_table_with_expected_columns(db_conn):
    rows = db_conn.execute("PRAGMA table_info(appointments)").fetchall()
    columns = {r["name"]: (r["type"], r["notnull"]) for r in rows}

    assert set(columns) == {
        "id",
        "appointment_date",
        "start_time",
        "end_time",
        "name",
        "email",
        "attendees",
        "created_at",
    }
    assert columns["id"][0] == "INTEGER"
    for col in ("appointment_date", "start_time", "end_time", "name", "email", "created_at"):
        assert columns[col] == ("TEXT", 1), col
    assert columns["attendees"] == ("INTEGER", 1)


def test_unique_index_on_email_and_date_exists(db_conn):
    indexes = db_conn.execute("PRAGMA index_list(appointments)").fetchall()
    by_name = {r["name"]: r for r in indexes}

    assert "idx_email_date" in by_name
    assert by_name["idx_email_date"]["unique"] == 1
    cols = [r["name"] for r in db_conn.execute("PRAGMA index_info(idx_email_date)").fetchall()]
    assert cols == ["email", "appointment_date"]


def test_date_index_exists_and_is_not_unique(db_conn):
    indexes = db_conn.execute("PRAGMA index_list(appointments)").fetchall()
    by_name = {r["name"]: r for r in indexes}

    assert "idx_date" in by_name
    assert by_name["idx_date"]["unique"] == 0
    cols = [r["name"] for r in db_conn.execute("PRAGMA index_info(idx_date)").fetchall()]
    assert cols == ["appointment_date"]


def test_duplicate_email_same_day_rejected_at_db_level(db_conn):
    db_conn.execute(
        "INSERT INTO appointments (appointment_date, start_time, end_time, name, email, attendees, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("2026-12-01", "09:00", "10:00", "Alice", "alice@x.com", 1, "2026-08-24T09:00:00"),
    )
    db_conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO appointments (appointment_date, start_time, end_time, name, email, attendees, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("2026-12-01", "11:00", "12:00", "Alice Again", "alice@x.com", 2, "2026-08-24T09:05:00"),
        )


def test_same_email_different_day_allowed_at_db_level(db_conn):
    db_conn.execute(
        "INSERT INTO appointments (appointment_date, start_time, end_time, name, email, attendees, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("2026-12-01", "09:00", "10:00", "Alice", "alice@x.com", 1, "2026-08-24T09:00:00"),
    )
    db_conn.execute(
        "INSERT INTO appointments (appointment_date, start_time, end_time, name, email, attendees, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("2026-12-02", "09:00", "10:00", "Alice", "alice@x.com", 1, "2026-08-24T09:00:00"),
    )
    db_conn.commit()

    count = db_conn.execute("SELECT COUNT(*) AS n FROM appointments").fetchone()["n"]
    assert count == 2


def test_db_path_comes_from_environment(monkeypatch):
    monkeypatch.setenv("APPOINTMENTS_DB", "Z:/custom/path.db")
    assert db.get_db_path() == "Z:/custom/path.db"

    monkeypatch.delenv("APPOINTMENTS_DB", raising=False)
    assert db.get_db_path() == db.DEFAULT_DB_PATH


def test_post_route_is_registered(client):
    routes = {getattr(r, "path", None) for r in client.app.routes}
    assert "/appointments" in routes
