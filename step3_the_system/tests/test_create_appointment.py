def test_valid_booking_returns_201_with_created_record(client, booking_payload, future_dow):
    resp = client.post(
        "/appointments",
        json=booking_payload(date=future_dow(0), attendees=3),
    )

    assert resp.status_code == 201
    body = resp.json()
    assert isinstance(body["id"], int)
    assert body["name"] == "Alice"
    assert body["attendees"] == 3


def test_missing_attendees_defaults_to_1(client, booking_payload, future_dow):
    resp = client.post("/appointments", json=booking_payload(date=future_dow(0)))

    assert resp.status_code == 201
    assert resp.json()["attendees"] == 1


def test_email_normalized_in_response(client, booking_payload, future_dow):
    resp = client.post(
        "/appointments",
        json=booking_payload(date=future_dow(0), email="  ALICE@X.COM  "),
    )

    assert resp.status_code == 201
    assert resp.json()["email"] == "alice@x.com"


def test_booking_persisted_to_database(client, booking_payload, db_conn, future_dow):
    day = future_dow(2)
    resp = client.post(
        "/appointments",
        json=booking_payload(
            date=day,
            start_time="10:00",
            end_time="11:00",
            name="  Bob  ",
            email="BOB@X.com",
            attendees=5,
        ),
    )

    assert resp.status_code == 201
    row = db_conn.execute("SELECT * FROM appointments WHERE id = ?", (resp.json()["id"],)).fetchone()
    assert row is not None
    assert row["appointment_date"] == day
    assert row["start_time"] == "10:00"
    assert row["end_time"] == "11:00"
    assert row["name"] == "Bob"
    assert row["email"] == "bob@x.com"
    assert row["attendees"] == 5
    assert row["created_at"]
