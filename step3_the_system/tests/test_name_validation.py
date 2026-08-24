VALID_NAME = {"name": "Alice"}


def _body(resp):
    return resp.json()


def test_missing_name_rejected_with_name_required(client):
    resp = client.post("/appointments", json={})

    assert resp.status_code == 400
    body = _body(resp)
    assert body["error"]["code"] == "NAME_REQUIRED"
    assert isinstance(body["error"]["message"], str)


def test_empty_name_rejected_with_name_required(client):
    resp = client.post("/appointments", json={"name": ""})

    assert resp.status_code == 400
    assert _body(resp)["error"]["code"] == "NAME_REQUIRED"


def test_whitespace_only_name_rejected_as_empty(client):
    resp = client.post("/appointments", json={"name": "   "})

    assert resp.status_code == 400
    assert _body(resp)["error"]["code"] == "NAME_REQUIRED"


def test_error_body_matches_constitution_shape(client):
    resp = client.post("/appointments", json={})

    body = _body(resp)
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message"}


def test_valid_name_passes_name_check(client, booking_payload):
    resp = client.post("/appointments", json=booking_payload())

    assert resp.json().get("error", {}).get("code") != "NAME_REQUIRED"
