SEED_EMAIL = "seed@x.com"


def _code(resp):
    return resp.json().get("error", {}).get("code")


def _seed(conn, day, start, end):
    conn.execute(
        "INSERT INTO appointments (appointment_date, start_time, end_time, name, email, attendees, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (day, start, end, "Seed", SEED_EMAIL, 1, "2026-01-01T00:00:00"),
    )
    conn.commit()


def test_exact_match_rejected(client, booking_payload, db_conn, future_dow):
    day = future_dow(0)
    _seed(db_conn, day, "08:00", "09:00")
    resp = client.post(
        "/appointments", json=booking_payload(date=day, start_time="08:00", end_time="09:00")
    )

    assert resp.status_code == 400
    assert _code(resp) == "SLOT_OVERLAP"


def test_partial_overlap_at_start_rejected(client, booking_payload, db_conn, future_dow):
    day = future_dow(0)
    _seed(db_conn, day, "09:00", "10:00")
    resp = client.post(
        "/appointments", json=booking_payload(date=day, start_time="08:30", end_time="09:30")
    )

    assert resp.status_code == 400
    assert _code(resp) == "SLOT_OVERLAP"


def test_partial_overlap_at_end_rejected(client, booking_payload, db_conn, future_dow):
    day = future_dow(0)
    _seed(db_conn, day, "09:00", "10:00")
    resp = client.post(
        "/appointments", json=booking_payload(date=day, start_time="09:30", end_time="10:30")
    )

    assert resp.status_code == 400
    assert _code(resp) == "SLOT_OVERLAP"


def test_booking_containing_existing_rejected(client, booking_payload, db_conn, future_dow):
    day = future_dow(1)
    _seed(db_conn, day, "10:00", "11:00")
    resp = client.post(
        "/appointments", json=booking_payload(date=day, start_time="09:30", end_time="11:30")
    )

    assert resp.status_code == 400
    assert _code(resp) == "SLOT_OVERLAP"


def test_back_to_back_allowed(client, booking_payload, db_conn, future_dow):
    day = future_dow(0)
    _seed(db_conn, day, "08:00", "09:00")
    resp = client.post(
        "/appointments", json=booking_payload(date=day, start_time="09:00", end_time="11:00")
    )

    assert resp.status_code == 201


def test_different_day_allowed(client, booking_payload, db_conn, future_dow):
    _seed(db_conn, future_dow(0), "08:00", "09:00")
    resp = client.post(
        "/appointments",
        json=booking_payload(date=future_dow(1), start_time="08:00", end_time="09:00"),
    )

    assert resp.status_code == 201
