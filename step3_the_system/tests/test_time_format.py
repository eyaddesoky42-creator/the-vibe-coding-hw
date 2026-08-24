def _code(resp):
    return resp.json().get("error", {}).get("code")


def test_missing_start_and_end_rejected(client, booking_payload):
    payload = booking_payload()
    payload.pop("start_time")
    payload.pop("end_time")
    resp = client.post("/appointments", json=payload)

    assert resp.status_code == 400
    assert _code(resp) == "TIME_FORMAT_INVALID"


def test_single_digit_hour_rejected(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(start_time="9:00"))

    assert resp.status_code == 400
    assert _code(resp) == "TIME_FORMAT_INVALID"


def test_minute_out_of_range_rejected(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(end_time="10:60"))

    assert resp.status_code == 400
    assert _code(resp) == "TIME_FORMAT_INVALID"


def test_hour_out_of_range_rejected(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(start_time="25:00"))

    assert resp.status_code == 400
    assert _code(resp) == "TIME_FORMAT_INVALID"


def test_missing_colon_rejected(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(start_time="0900"))

    assert resp.status_code == 400
    assert _code(resp) == "TIME_FORMAT_INVALID"


def test_valid_times_pass_check(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload())

    assert _code(resp) != "TIME_FORMAT_INVALID"
