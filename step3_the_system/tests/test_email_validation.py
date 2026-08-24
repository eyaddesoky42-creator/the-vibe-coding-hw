def _code(resp):
    return resp.json().get("error", {}).get("code")


def test_missing_email_rejected_with_email_required(client, booking_payload):
    payload = booking_payload()
    payload.pop("email")
    resp = client.post("/appointments", json=payload)

    assert resp.status_code == 400
    assert _code(resp) == "EMAIL_REQUIRED"


def test_empty_email_rejected_with_email_required(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(email=""))

    assert resp.status_code == 400
    assert _code(resp) == "EMAIL_REQUIRED"


def test_whitespace_only_email_rejected_as_empty(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(email="   "))

    assert resp.status_code == 400
    assert _code(resp) == "EMAIL_REQUIRED"


def test_email_without_at_rejected_with_email_invalid(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(email="not-an-email"))

    assert resp.status_code == 400
    assert _code(resp) == "EMAIL_INVALID"


def test_valid_email_passes_email_check(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload())

    code = resp.json().get("error", {}).get("code")
    assert resp.status_code != 400
    assert code != "EMAIL_REQUIRED"
    assert code != "EMAIL_INVALID"


def test_mixed_case_and_spaces_email_passes_check(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(email="  ALICE@X.COM  "))

    assert resp.status_code != 400
