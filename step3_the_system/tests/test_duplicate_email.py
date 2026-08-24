def _code(resp):
    return resp.json().get("error", {}).get("code")


def _seed(conn, day, start, end, email):
    conn.execute(
        "INSERT INTO appointments (appointment_date, start_time, end_time, name, email, attendees, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (day, start, end, "Seed", email, 1, "2026-01-01T00:00:00"),
    )
    conn.commit()


def test_same_email_same_day_rejected(client, booking_payload, db_conn, future_dow):
    day = future_dow(0)
    _seed(db_conn, day, "11:00", "12:00", "alice@x.com")
    resp = client.post("/appointments", json=booking_payload(date=day))

    assert resp.status_code == 400
    assert _code(resp) == "DUPLICATE_EMAIL_SAME_DAY"


def test_case_and_whitespace_insensitive_rejection(client, booking_payload, db_conn, future_dow):
    day = future_dow(0)
    _seed(db_conn, day, "11:00", "12:00", "alice@x.com")
    resp = client.post(
        "/appointments", json=booking_payload(date=day, email="  ALICE@X.COM  ")
    )

    assert resp.status_code == 400
    assert _code(resp) == "DUPLICATE_EMAIL_SAME_DAY"


def test_same_email_different_day_allowed(client, booking_payload, db_conn, future_dow):
    _seed(db_conn, future_dow(0), "09:00", "10:00", "alice@x.com")
    resp = client.post("/appointments", json=booking_payload(date=future_dow(1)))

    assert resp.status_code == 201


def test_different_email_same_day_allowed(client, booking_payload, db_conn, future_dow):
    day = future_dow(0)
    _seed(db_conn, day, "08:00", "09:00", "bob@x.com")
    resp = client.post(
        "/appointments",
        json=booking_payload(date=day, start_time="10:00", end_time="11:00"),
    )

    assert resp.status_code == 201
