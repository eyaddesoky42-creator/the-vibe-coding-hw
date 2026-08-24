def _code(resp):
    return resp.json().get("error", {}).get("code")


def test_start_before_opening_rejected(client, booking_payload, future_dow):
    resp = client.post(
        "/appointments",
        json=booking_payload(date=future_dow(6), start_time="07:00", end_time="08:00"),
    )

    assert resp.status_code == 400
    assert _code(resp) == "OUTSIDE_BUSINESS_HOURS"


def test_end_after_closing_rejected(client, booking_payload, future_dow):
    monday = future_dow(0)
    resp = client.post(
        "/appointments",
        json=booking_payload(date=monday, start_time="17:30", end_time="18:30"),
    )

    assert resp.status_code == 400
    assert _code(resp) == "OUTSIDE_BUSINESS_HOURS"


def test_entirely_outside_hours_rejected(client, booking_payload, future_dow):
    resp = client.post(
        "/appointments",
        json=booking_payload(date=future_dow(1), start_time="06:00", end_time="07:00"),
    )

    assert resp.status_code == 400
    assert _code(resp) == "OUTSIDE_BUSINESS_HOURS"


def test_start_exactly_at_opening_allowed(client, booking_payload, future_dow):
    resp = client.post(
        "/appointments",
        json=booking_payload(date=future_dow(2), start_time="08:00", end_time="09:00"),
    )

    assert resp.status_code == 201


def test_end_exactly_at_closing_allowed(client, booking_payload, future_dow):
    resp = client.post(
        "/appointments",
        json=booking_payload(date=future_dow(3), start_time="17:00", end_time="18:00"),
    )

    assert resp.status_code == 201


def test_within_hours_passes_check(client, booking_payload, future_dow):
    resp = client.post(
        "/appointments",
        json=booking_payload(date=future_dow(0), start_time="09:00", end_time="10:00"),
    )

    assert resp.status_code == 201
