def _code(resp):
    return resp.json().get("error", {}).get("code")


def test_friday_rejected(client, booking_payload, future_dow):
    resp = client.post("/appointments", json=booking_payload(date=future_dow(4)))

    assert resp.status_code == 400
    assert _code(resp) == "CLOSED_DAY"


def test_saturday_rejected(client, booking_payload, future_dow):
    resp = client.post("/appointments", json=booking_payload(date=future_dow(5)))

    assert resp.status_code == 400
    assert _code(resp) == "CLOSED_DAY"


def test_monday_passes_closed_day_check(client, booking_payload, future_dow):
    resp = client.post("/appointments", json=booking_payload(date=future_dow(0)))

    assert _code(resp) != "CLOSED_DAY"


def test_sunday_passes_closed_day_check(client, booking_payload, future_dow):
    resp = client.post("/appointments", json=booking_payload(date=future_dow(6)))

    assert _code(resp) != "CLOSED_DAY"
