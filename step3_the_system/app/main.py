import os
import re
from contextlib import asynccontextmanager
from datetime import date, datetime, time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import db

TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class BookingRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    attendees: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    date: str | None = None


@asynccontextmanager
async def lifespan(application: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Appointment Booking Service", lifespan=lifespan)


def error_response(code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": {"code": code, "message": message}},
    )


def validate_name(booking: BookingRequest, values: dict) -> JSONResponse | None:
    name = (booking.name or "").strip()
    if not name:
        return error_response("NAME_REQUIRED", "name is required")
    values["name"] = name
    return None


def validate_email(booking: BookingRequest, values: dict) -> JSONResponse | None:
    email = (booking.email or "").strip().lower()
    if not email:
        return error_response("EMAIL_REQUIRED", "email is required")
    if "@" not in email:
        return error_response("EMAIL_INVALID", "email must contain '@'")
    values["email"] = email
    return None


def validate_attendees(booking: BookingRequest, values: dict) -> JSONResponse | None:
    if booking.attendees is not None:
        if booking.attendees < 1:
            return error_response("ATTENDEES_INVALID", "attendees must be at least 1")
        values["attendees"] = booking.attendees
    return None


def validate_time_format(booking: BookingRequest, values: dict) -> JSONResponse | None:
    start = booking.start_time or ""
    end = booking.end_time or ""
    if not TIME_RE.match(start) or not TIME_RE.match(end):
        return error_response(
            "TIME_FORMAT_INVALID", "start_time and end_time must be HH:MM (24-hour)"
        )
    values["start_time"] = start
    values["end_time"] = end
    values["start_t"] = datetime.strptime(start, "%H:%M").time()
    values["end_t"] = datetime.strptime(end, "%H:%M").time()
    return None


def validate_end_after_start(booking: BookingRequest, values: dict) -> JSONResponse | None:
    if values["end_t"] <= values["start_t"]:
        return error_response("END_NOT_AFTER_START", "end_time must be after start_time")
    return None


def validate_date_format(booking: BookingRequest, values: dict) -> JSONResponse | None:
    raw = booking.date or ""
    if not DATE_RE.match(raw):
        return error_response("DATE_INVALID", "date must be a real calendar date (YYYY-MM-DD)")
    try:
        parsed = date.fromisoformat(raw)
    except ValueError:
        return error_response("DATE_INVALID", "date must be a real calendar date (YYYY-MM-DD)")
    values["date"] = raw
    values["date_obj"] = parsed
    return None


def get_now() -> datetime:
    return datetime.now()


def _one_year_later(d: date) -> date:
    try:
        return d.replace(year=d.year + 1)
    except ValueError:
        return d.replace(year=d.year + 1, day=28)


def validate_date_range(booking: BookingRequest, values: dict) -> JSONResponse | None:
    today = get_now().date()
    d = values["date_obj"]
    if d < today or d > _one_year_later(today):
        return error_response("DATE_OUT_OF_RANGE", "date must be between today and one year from today")
    return None


def validate_closed_day(booking: BookingRequest, values: dict) -> JSONResponse | None:
    if values["date_obj"].weekday() in (4, 5):
        return error_response(
            "CLOSED_DAY", "appointments can only be booked Sunday through Thursday"
        )
    return None


def validate_business_hours(booking: BookingRequest, values: dict) -> JSONResponse | None:
    opening = time(8, 0)
    closing = time(18, 0)
    if not (opening <= values["start_t"] <= closing) or not (
        opening <= values["end_t"] <= closing
    ):
        return error_response(
            "OUTSIDE_BUSINESS_HOURS",
            "appointments must start and end between 08:00 and 18:00",
        )
    return None


def validate_lead_time(booking: BookingRequest, values: dict) -> JSONResponse | None:
    start_dt = datetime.combine(values["date_obj"], values["start_t"])
    if (start_dt - get_now()).total_seconds() < 2 * 3600:
        return error_response(
            "LEAD_TIME_TOO_SOON", "appointments must start at least 2 hours from now"
        )
    return None


def validate_overlap(booking: BookingRequest, values: dict) -> JSONResponse | None:
    conn = db.get_connection()
    try:
        row = conn.execute(
            "SELECT 1 FROM appointments WHERE appointment_date = ? AND start_time < ? AND end_time > ?",
            (values["date"], values["end_time"], values["start_time"]),
        ).fetchone()
    finally:
        conn.close()
    if row is not None:
        return error_response(
            "SLOT_OVERLAP", "the requested time overlaps an existing appointment"
        )
    return None


def validate_duplicate_email(booking: BookingRequest, values: dict) -> JSONResponse | None:
    conn = db.get_connection()
    try:
        row = conn.execute(
            "SELECT 1 FROM appointments WHERE email = ? AND appointment_date = ?",
            (values["email"], values["date"]),
        ).fetchone()
    finally:
        conn.close()
    if row is not None:
        return error_response(
            "DUPLICATE_EMAIL_SAME_DAY",
            "this email already has an appointment on that date",
        )
    return None


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response("VALIDATION_ERROR", "request body is invalid or malformed")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": str(exc.detail)}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "unexpected server error"}},
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.environ.get("APP_HOST", "127.0.0.1"),
        port=int(os.environ.get("APP_PORT", "8000")),
    )


@app.post("/appointments")
def create_appointment(booking: BookingRequest):
    values: dict = {}
    checks = (
        validate_name,
        validate_email,
        validate_attendees,
        validate_time_format,
        validate_end_after_start,
        validate_date_format,
        validate_date_range,
        validate_closed_day,
        validate_business_hours,
        validate_lead_time,
        validate_overlap,
        validate_duplicate_email,
    )
    for check in checks:
        if (err := check(booking, values)) is not None:
            return err
    attendees = values.get("attendees", 1)
    conn = db.get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO appointments (appointment_date, start_time, end_time, name, email, attendees, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                values["date"],
                values["start_time"],
                values["end_time"],
                values["name"],
                values["email"],
                attendees,
                get_now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        appointment_id = cursor.lastrowid
    finally:
        conn.close()
    return JSONResponse(
        status_code=201,
        content={
            "id": appointment_id,
            "date": values["date"],
            "start_time": values["start_time"],
            "end_time": values["end_time"],
            "name": values["name"],
            "email": values["email"],
            "attendees": attendees,
        },
    )
