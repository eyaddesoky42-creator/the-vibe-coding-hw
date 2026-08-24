from datetime import datetime


BOOKING_TIME = datetime(2026, 9, 1, 9, 0, 0)


def _code(resp):
    return resp.json().get("error", {}).get("code")


def test_start_one_hour_away_rejected(client, booking_payload, freeze_clock):
    freeze_clock(BOOKING_TIME)
    resp = client.post(
        "/appointments",
        json=booking_payload(date="2026-09-01", start_time="10:00", end_time="11:00"),
    )

    assert resp.status_code == 400
    assert _code(resp) == "LEAD_TIME_TOO_SOON"


def test_start_less_than_hour_away_rejected(client, booking_payload, freeze_clock):
    freeze_clock(BOOKING_TIME)
    resp = client.post(
        "/appointments",
        json=booking_payload(date="2026-09-01", start_time="09:30", end_time="10:30"),
    )

    assert resp.status_code == 400
    assert _code(resp) == "LEAD_TIME_TOO_SOON"


def test_start_exactly_two_hours_away_allowed(client, booking_payload, freeze_clock):
    freeze_clock(BOOKING_TIME)
    resp = client.post(
        "/appointments",
        json=booking_payload(date="2026-09-01", start_time="11:00", end_time="12:00"),
    )

    assert resp.status_code == 201


def test_next_day_start_allowed(client, booking_payload, freeze_clock):
    freeze_clock(BOOKING_TIME)
    resp = client.post(
        "/appointments",
        json=booking_payload(date="2026-09-02", start_time="10:00", end_time="11:00"),
    )

    assert resp.status_code == 201


def test_date_range_uses_injected_clock(client, booking_payload, freeze_clock):
    freeze_clock(BOOKING_TIME)
    resp = client.post(
        "/appointments",
        json=booking_payload(date="2027-08-01", start_time="10:00", end_time="11:00"),
    )

    assert resp.status_code == 201
