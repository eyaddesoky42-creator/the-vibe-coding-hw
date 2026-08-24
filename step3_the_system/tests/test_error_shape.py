def _shape_ok(body):
    return set(body) == {"error"} and set(body["error"]) == {"code", "message"}


def test_malformed_json_returns_validation_error(client):
    resp = client.post(
        "/appointments",
        content="{not valid json",
        headers={"Content-Type": "application/json"},
    )

    assert resp.status_code == 400
    body = resp.json()
    assert _shape_ok(body)
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_wrong_field_type_returns_validation_error(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload(attendees="two"))

    assert resp.status_code == 400
    body = resp.json()
    assert _shape_ok(body)
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_missing_body_returns_validation_error(client):
    resp = client.post("/appointments")

    assert resp.status_code == 400
    body = resp.json()
    assert _shape_ok(body)
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_unknown_route_returns_error_shape(client):
    resp = client.get("/definitely-not-a-route")

    assert resp.status_code == 404
    body = resp.json()
    assert _shape_ok(body)


def test_valid_booking_still_works_with_handlers(client, booking_payload, future_dow):
    resp = client.post("/appointments", json=booking_payload(date=future_dow(0)))

    assert resp.status_code == 201
