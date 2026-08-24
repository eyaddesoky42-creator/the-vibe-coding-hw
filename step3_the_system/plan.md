# plan.md — Appointment Booking Service

Trace tags: `FR-x` / `AC-x` = spec.md; `C1..C7` = constitution.md line numbers (C1 stack, C2 dep justification, C3 test rule, C4 error shape, C5 boundary validation, C6 env config, C7 Definition of Done).

## 1. STACK

Mandated by constitution.md baseline (C1):

- **Python 3.11+** — [C1] language baseline.
- **FastAPI** — [C1] HTTP framework. Its bundled dependency **pydantic v2** is used for request models (boundary validation, C5); it ships with FastAPI, so it is not a separate install.
- **pytest** — [C1] test runner. Tests use `fastapi.testclient.TestClient`, exercising real HTTP paths per C3.

NEW DEPENDENCY — flagged per C2:

- **uvicorn** (NEW DEPENDENCY) — because FastAPI is only an ASGI application framework; an ASGI server is required to serve HTTP at all.
- **httpx** (NEW DEPENDENCY) — because Starlette's `TestClient` (what `fastapi.testclient` wraps) requires httpx; needed to run the C3-mandated pytest tests.

Standard library only (no NEW DEPENDENCY): `sqlite3`, `datetime`, `os.environ`. Explicitly rejected: ORMs, `python-dateutil`, `pydantic-settings` — every job they'd do is covered by stdlib + pydantic-already-bundled, and C2 forbids silent additions.

Config: DB path and host/port read from environment variables (`APPOINTMENTS_DB`, `APP_HOST`, `APP_PORT`) with sane defaults. [C6, C7 — no secrets in code]

## 2. DATA MODEL

**Storage: SQLite, single file, via stdlib `sqlite3`.**
Because: C1/C2 give us no database library, and spec.md describes a "small, single-user app" with race conditions declared a NON-GOAL — a stdlib file-backed DB satisfies every FR (persistence, uniqueness, range queries) with zero new dependencies. In-memory was rejected because it loses bookings on restart for no benefit.

Table `appointments`:

| column | type | notes |
|---|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | returned to caller |
| `appointment_date` | TEXT NOT NULL | ISO `YYYY-MM-DD`; text sorts chronologically |
| `start_time` | TEXT NOT NULL | 24h `HH:MM` |
| `end_time` | TEXT NOT NULL | 24h `HH:MM` |
| `name` | TEXT NOT NULL | trimmed at boundary [AC-2] |
| `email` | TEXT NOT NULL | normalized: trimmed + lowercased before insert [FR-3, AC-23] |
| `attendees` | INTEGER NOT NULL | boundary applies default 1 [FR-1, AC-4] |
| `created_at` | TEXT NOT NULL | ISO timestamp of when the booking was made (audit trail for FR-4 reasoning) |

Indexes:

- `UNIQUE INDEX idx_email_date ON appointments(email, appointment_date)` — enforces FR-3 at the storage layer, not just in code [FR-3].
- `INDEX idx_date ON appointments(appointment_date)` — overlap check scans one day [FR-2].

Core queries:

- Overlap (FR-2): `SELECT ... WHERE appointment_date = ? AND start_time < :end AND end_time > :start` — half-open interval math makes back-to-back bookings (AC-8) pass and exact/partial overlap (AC-5, AC-6) fail.
- Duplicate (FR-3): satisfied by the unique index lookup on `(normalized_email, date)`.

## 3. API CONTRACTS

All FRs are constraints on creating a booking, so the surface is one endpoint. No list/cancel endpoints — spec.md defines none, and adding one would be scope creep.

```
Contract: POST /appointments
          {date:"YYYY-MM-DD", start_time:"HH:MM", end_time:"HH:MM",
           name:string, email:string, attendees?:integer=1}   [FR-1, AC-4]
          → 201 {id:int, date:"YYYY-MM-DD", start_time:"HH:MM",
                 end_time:"HH:MM", name:string, email:string, attendees:int}   [AC-1]
          → 400 {"error":{"code":"...","message":"..."}}                        [C4]
```

Error codes (every FR maps to at least one):

| code | trigger | trace |
|---|---|---|
| `NAME_REQUIRED` | missing/empty name | FR-1, AC-2 |
| `EMAIL_REQUIRED` | missing/empty email | FR-1, AC-3 |
| `EMAIL_INVALID` | non-empty but lacks "@" | FR-1 (see RISKS #2) |
| `ATTENDEES_INVALID` | not an integer or < 1 | FR-1 (see RISKS #1) |
| `DATE_INVALID` | not a real calendar date (e.g. `2026-06-31`) | FR-1, AC-20 |
| `DATE_OUT_OF_RANGE` | date in the past or > 1 year out | FR-1, AC-21 (AC-22 passes) |
| `TIME_FORMAT_INVALID` | start/end not parseable `HH:MM` | FR-1 |
| `END_NOT_AFTER_START` | end ≤ start | FR-1 (see RISKS #5) |
| `CLOSED_DAY` | Friday or Saturday | FR-5, AC-15, AC-16 |
| `OUTSIDE_BUSINESS_HOURS` | start or end outside 08:00–18:00 inclusive | FR-5, AC-17, AC-18 (AC-19 passes) |
| `LEAD_TIME_TOO_SOON` | start < 2h from booking instant | FR-4, AC-12 (AC-13, AC-14 pass) |
| `SLOT_OVERLAP` | exact/partial overlap on same date | FR-2, AC-5, AC-6 (AC-7, AC-8 pass) |
| `DUPLICATE_EMAIL_SAME_DAY` | normalized email already booked that date | FR-3, AC-10, AC-23 (AC-9, AC-11 pass) |

Malformed JSON / wrong types from FastAPI's parser are re-wrapped by a global exception handler into the C4 shape with `VALIDATION_ERROR` — never a raw 422 `{"detail": ...}` and never a stack trace [C4, C5].

Tests (per C3): each endpoint gets one happy-path test (201, AC-1) and one error-path test per error code above, using an injected fake clock to pin "now" for FR-4 cases deterministically.

## 4. RISKS

1. **Attendee min/max unspecified** ([NEEDS CLARIFICATION]) — decided: integer ≥ 1, no upper bound — because the default of 1 implies counting people, so 0/negatives are nonsensical; spec sets no cap so none invented.
2. **Email format depth** ([NEEDS CLARIFICATION]) — decided: non-empty + must contain "@" (no full RFC regex) — because AC-3 only mandates rejecting empty, and over-validating risks rejecting valid users spec never excluded.
3. **Minute granularity** ([NEEDS CLARIFICATION]) — decided: any `HH:MM` accepted, no slot grid — because spec never mentions increments; adding a grid would invent a rule.
4. **Boundary inclusivity of hours** ([NEEDS CLARIFICATION]) — decided: inclusive (start 08:00 and end 18:00 allowed) — because "between 8 AM and 6 PM" reads inclusive and AC-17/AC-18 only reject strictly-outside times.
5. **Zero-length / reversed bookings** ([NEEDS CLARIFICATION]) — decided: explicitly rejected via `END_NOT_AFTER_START`; no other min/max duration — because end ≤ start breaks overlap math and no duration limits exist anywhere in spec.
6. **Exact 1-year boundary** — decided: allowed through the same calendar date next year (year+1 arithmetic; Feb 29 → Feb 28 fallback) — because AC-21/AC-22 leave only the exact-boundary day open, and calendar arithmetic matches "within 1 year".
7. **Is "today" past?** — decided: today is bookable (subject to FR-4's 2-hour lead) — because FR-1 says "in the past" and FR-4 already governs same-day near-term slots; double-rejecting today would make FR-4 redundant.
8. **Timezone** — decided: naive local server time everywhere (dates, times, "now") — because spec never names a timezone and this is a single-region scheduling app.
9. **Deterministic FR-4 tests** — decided: clock injected as a callable, defaulting to `datetime.now()` — because AC-12–14 fix "booking time" to arbitrary instants; wall-clock tests would be flaky (C7: tests must pass reliably).
10. **Error precedence when multiple rules fail** — decided: fixed order — field formats → date validity/range → closed day → business hours → lead time → overlap → duplicate email — because spec doesn't rank errors; a deterministic order keeps AC tests stable.
11. **Name content rules** — decided: any non-empty string after trimming, no length cap — because spec only specifies "missing or empty" as invalid (AC-2); anything more is invention.
12. **Simultaneous duplicate bookings** — acknowledged NON-GOAL per spec; SQLite's unique index will still make one request win rather than corrupt data, but no explicit locking built.
