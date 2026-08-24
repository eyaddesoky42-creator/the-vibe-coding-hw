import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient


@pytest.fixture()
def future_dow():
    def _make(weekday: int, min_days: int = 30):
        assert 0 <= weekday <= 6
        today = date.today()
        delta = (weekday - today.weekday()) % 7
        while delta < min_days:
            delta += 7
        return (today + timedelta(days=delta)).isoformat()

    return _make


@pytest.fixture()
def booking_payload():
    def _make(**overrides):
        payload = {
            "name": "Alice",
            "email": "alice@x.com",
            "date": "2027-08-02",
            "start_time": "09:00",
            "end_time": "10:00",
        }
        payload.update(overrides)
        return payload

    return _make


@pytest.fixture()
def freeze_clock(monkeypatch):
    def _set(dt):
        monkeypatch.setattr("app.main.get_now", lambda: dt)

    return _set


@pytest.fixture()
def db_conn(tmp_path, monkeypatch):
    monkeypatch.setenv("APPOINTMENTS_DB", str(tmp_path / "test_appointments.db"))
    from app import db

    conn = db.get_connection()
    db.init_db(conn)
    yield conn
    conn.close()


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("APPOINTMENTS_DB", str(tmp_path / "test_appointments.db"))
    from app.main import app

    with TestClient(app) as c:
        yield c
