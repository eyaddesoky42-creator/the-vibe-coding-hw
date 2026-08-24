from datetime import date, datetime, timedelta


def _code(resp):
    return resp.json().get("error", {}).get("code")


def _one_year_later(d):
    try:
        return d.replace(year=d.year + 1)
    except ValueError:
        return d.replace(year=d.year + 1, day=28)


FROZEN_NOW = datetime(2026, 9, 1, 9, 0, 0)


def test_past_date_rejected(client, booking_payload, future_dow):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    resp = client.post("/appointments", json=booking_payload(date=yesterday))

    assert resp.status_code == 400
    assert _code(resp) == "DATE_OUT_OF_RANGE"


def test_far_future_date_rejected(client, booking_payload):
    far = (date.today() + timedelta(days=400)).isoformat()
    resp = client.post("/appointments", json=booking_payload(date=far))

    assert resp.status_code == 400
    assert _code(resp) == "DATE_OUT_OF_RANGE"


def test_one_day_past_one_year_boundary_rejected(client, booking_payload, freeze_clock):
    freeze_clock(FROZEN_NOW)
    beyond = (_one_year_later(FROZEN_NOW.date()) + timedelta(days=1)).isoformat()
    resp = client.post("/appointments", json=booking_payload(date=beyond))

    assert resp.status_code == 400
    assert _code(resp) == "DATE_OUT_OF_RANGE"


def test_today_passes_range_check(client, booking_payload, freeze_clock):
    freeze_clock(FROZEN_NOW)
    resp = client.post(
        "/appointments",
        json=booking_payload(date="2026-09-01", start_time="11:00", end_time="12:00"),
    )

    assert resp.status_code == 201


def test_exact_one_year_boundary_passes(client, booking_payload, freeze_clock):
    freeze_clock(FROZEN_NOW)
    edge = _one_year_later(FROZEN_NOW.date()).isoformat()
    resp = client.post(
        "/appointments",
        json=booking_payload(date=edge, start_time="11:00", end_time="12:00"),
    )

    assert resp.status_code == 201
