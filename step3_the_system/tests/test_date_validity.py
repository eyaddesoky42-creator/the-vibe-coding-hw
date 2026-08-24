def _code(resp):
    return resp.json().get("error", {}).get("code")


def test_nonexistent_calendar_date_rejected(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(date="2026-06-31"))

    assert resp.status_code == 400
    assert _code(resp) == "DATE_INVALID"


def test_wrong_separator_rejected(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(date="2026/12/01"))

    assert resp.status_code == 400
    assert _code(resp) == "DATE_INVALID"


def test_single_digit_month_rejected(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(date="2027-8-02"))

    assert resp.status_code == 400
    assert _code(resp) == "DATE_INVALID"


def test_compact_iso_format_rejected(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(date="20270802"))

    assert resp.status_code == 400
    assert _code(resp) == "DATE_INVALID"


def test_missing_date_rejected(client, booking_payload):
    payload = booking_payload()
    payload.pop("date")
    resp = client.post("/appointments", json=payload)

    assert resp.status_code == 400
    assert _code(resp) == "DATE_INVALID"


def test_real_date_passes_check(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(date="2027-08-02"))

    assert _code(resp) != "DATE_INVALID"
