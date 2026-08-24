def _code(resp):
    return resp.json().get("error", {}).get("code")


def test_end_equal_to_start_rejected(client, booking_payload):
    resp = client.post(
        "/appointments", json=booking_payload(start_time="10:00", end_time="10:00")
    )

    assert resp.status_code == 400
    assert _code(resp) == "END_NOT_AFTER_START"


def test_end_before_start_rejected(client, booking_payload):
    resp = client.post(
        "/appointments", json=booking_payload(start_time="15:00", end_time="14:00")
    )

    assert resp.status_code == 400
    assert _code(resp) == "END_NOT_AFTER_START"


def test_end_after_start_passes_check(client, booking_payload):
    resp = client.post(
        "/appointments", json=booking_payload(start_time="09:00", end_time="09:01")
    )

    assert _code(resp) != "END_NOT_AFTER_START"
