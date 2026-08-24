def _code(resp):
    return resp.json().get("error", {}).get("code")


def test_zero_attendees_rejected(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(attendees=0))

    assert resp.status_code == 400
    assert _code(resp) == "ATTENDEES_INVALID"


def test_negative_attendees_rejected(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(attendees=-3))

    assert resp.status_code == 400
    assert _code(resp) == "ATTENDEES_INVALID"


def test_absent_attendees_passes_check(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload())

    assert _code(resp) != "ATTENDEES_INVALID"


def test_positive_attendees_passes_check(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(attendees=4))

    assert _code(resp) != "ATTENDEES_INVALID"
