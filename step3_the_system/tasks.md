# tasks.md — Appointment Booking Service

Derived from plan.md. Task order follows plan.md RISK #10 precedence: field formats → date validity/range → closed day → business hours → lead time → overlap → duplicate email → happy path → error-shape handler. Every task ships its tests with it (constitution C3).

T001  Scaffold FastAPI app with empty POST /appointments route + SQLite `appointments` table, `UNIQUE(email, appointment_date)` index, `idx_date` index, env-configured DB path
    Covers: FR-1 storage, FR-2 idx_date, FR-3 unique index, C6 env config (plan.md DATA MODEL)
    Test: tests/test_schema.py

T002 [P]  Reject missing/empty name (trim before checking); accept trimmed value downstream
    Covers: NAME_REQUIRED, FR-1 / AC-2
    Test: tests/test_name_validation.py
    Depends: T001

T003 [P]  Reject missing/empty email and email without "@"; normalize (trim + lowercase) for storage/comparison
    Covers: EMAIL_REQUIRED, EMAIL_INVALID, FR-1 / AC-3, FR-3 / AC-23 groundwork
    Test: tests/test_email_validation.py
    Depends: T001

T004 [P]  Reject provided attendees that are non-integer or < 1 (absent stays allowed until T014 applies default)
    Covers: ATTENDEES_INVALID, FR-1
    Test: tests/test_attendees_validation.py
    Depends: T001

T005 [P]  Reject start_time/end_time not parseable as 24h HH:MM
    Covers: TIME_FORMAT_INVALID, FR-1
    Test: tests/test_time_format.py
    Depends: T001

T006  Reject end_time <= start_time
    Covers: END_NOT_AFTER_START, FR-1 (plan.md RISKS #5)
    Test: tests/test_end_after_start.py
    Depends: T005

T007 [P]  Reject structurally valid strings that are not real calendar dates (e.g. 2026-06-31); strict YYYY-MM-DD parse
    Covers: DATE_INVALID, FR-1 / AC-20
    Test: tests/test_date_validity.py
    Depends: T001

T008  Reject dates in the past or beyond 1 year (calendar year+1 arithmetic, Feb-29 fallback; exact-boundary day allowed)
    Covers: DATE_OUT_OF_RANGE, FR-1 / AC-21 (AC-22 must pass)
    Test: tests/test_date_range.py
    Depends: T007

T009  Reject bookings on Friday/Saturday
    Covers: CLOSED_DAY, FR-5 / AC-15, AC-16
    Test: tests/test_closed_days.py
    Depends: T008

T010  Enforce 08:00–18:00 inclusive window on BOTH start_time and end_time
    Covers: OUTSIDE_BUSINESS_HOURS, FR-5 / AC-17, AC-18 (AC-19 must pass)
    Test: tests/test_business_hours.py
    Depends: T005, T009

T011  Introduce injectable clock (default datetime.now, plan.md RISKS #9) and reject starts sooner than 2h from booking instant
    Covers: LEAD_TIME_TOO_SOON, FR-4 / AC-12 (AC-13, AC-14 must pass)
    Test: tests/test_lead_time.py
    Depends: T010

T012  Reject exact/partial overlaps on same date via half-open interval query (back-to-back and different-day allowed)
    Covers: SLOT_OVERLAP, FR-2 / AC-5, AC-6 (AC-7, AC-8 must pass)
    Test: tests/test_overlap.py
    Depends: T011

T013  Reject second booking for same normalized email on same date (unique index backs the check)
    Covers: DUPLICATE_EMAIL_SAME_DAY, FR-3 / AC-10, AC-23 (AC-9, AC-11 must pass)
    Test: tests/test_duplicate_email.py
    Depends: T012

T014  Persist validated booking; apply attendees default 1 when absent; return 201 with id + echoed fields
    Covers: AC-1, AC-4, FR-1 happy path
    Test: tests/test_create_appointment.py
    Depends: T013

T015  Global exception handler: map malformed JSON / request-body type errors (FastAPI 422 path) to 400 {"error":{"code":"VALIDATION_ERROR",...}} — never a stack trace
    Covers: C4, C5, VALIDATION_ERROR
    Test: tests/test_error_shape.py
    Depends: T014
