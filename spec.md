FR-1  A user can book an appointment by providing:
      - a date
      - a start time
      - an end time
      - their name
      - at least one of: email, phone number
      - number of attendees (optional — defaults to 1 if not provided)

AC-1  Given valid values are provided for date, start time, end time, name,
      email, and number of attendees,
      when the user submits the booking,
      then the appointment is created successfully.

AC-2  Given the name is missing or empty,
      when the user submits the booking,
      then it is rejected with a validation error.
AC-3  Given the email is missing or empty,
      when the user submits the booking,
      then it is rejected with a validation error.
AC-4  Given the number of attendees is not provided,
      when the user submits the booking,
      then the appointment is created successfully with 1 attendee assigned.

FR-2  Booking a date and start/end time that overlaps with an existing appointment
      on the same date is rejected with an error. This includes exact
      slots and any partial overlap. Back-to-back bookings (one ending exactly
      when another starts) are NOT a conflict and are allowed.

AC-5  Given an appointment scheduled on 2026-12-01 from 08:00 to 09:00,
      when a user tries to book 2026-09-01 from 08:00 to 09:00 (exact match),
      then the booking is rejected with an error.

AC- 6 Given an appointment scheduled on 2026-12-01 from 08:00 to 09:00,
      when a user tries to book 2026-09-01 from 08:30 to 09:30 (partial overlap),
      then the booking is rejected with an error
AC-7  Given an appointment scheduled on 2026-12-01 from 08:00 to 09:00,
      when a user tries to book 2026-09-01 from 10:00 to 11:00 (empty schedule),
      then the booking succeeds.      
AC-8  Given an appointment scheduled on 2026-12-01 from 08:00 to 09:00,
      when a user tries to book 2026-09-01 from 09:00 to 11:00 (Back-to-back),
      then the booking succeeds.      
FR-3  A user (identified by email) cannot have more than one appointment on
      the same date. A booking attempt with an email that already has an
      appointment on that date is rejected with an error

AC-9  AC-9  Given [email protected] has an appointment on 2026-12-01,
      when [email protected] tries to book an appointment on 2026-12-02,
      then the booking succeeds.
AC-10  Given [email protected] has an appointment on 2026-12-01,
      when [email protected] tries to book an appointment on 2026-12-01,
      then the booking is rejected with an error
AC-11  Given [email protected] has an appointment on 2026-12-01,
      when [email protected] tries to book an appointment on 2026-12-01, (different email with no conflicts)
      then the booking succeeds.
FR-4  An appointment's start time must be at least 2 hours after the time of booking. 
      Bookings that start sooner than 2 hours from now are rejected with an error.
AC-12 Given the booking time is 2026-09-01 09:00,
      when a user tries to book an appointment starting at 2026-09-01 10:00
      (only 1 hour away),
      then the booking is rejected with an error.
AC-13 Given the booking time is 2026-09-01 09:00,
      when a user tries to book an appointment starting at 2026-09-01 11:00
      (2 hour away),
      then the booking succeeds.      
AC-14 Given the booking time is 2026-09-01 09:00,
      when a user tries to book an appointment starting at 2026-09-01 11:00
      (a day after, more than the 2 hours minimum),
      then the booking succeeds.
FR-5  Appointments can only be booked on Sunday through Thursday, between
      8:00 AM and 6:00 PM. Bookings on Friday, Saturday, or outside these
      hours are rejected with an error. Both the start time and the end
      time must fall within 8:00 AM–6:00 PM.

AC-15 Given a user tries to book an appointment on a Friday,
      when they submit the booking,
      then it is rejected with an error.

AC-16 Given a user tries to book an appointment on a Saturday,
      when they submit the booking,
      then it is rejected with an error.

AC-17 Given a user tries to book an appointment on a Sunday from 07:00 to 08:00
     (starts before opening),
      when they submit the booking,
      then it is rejected with an error.

AC-18 Given a user tries to book an appointment on a Monday from 17:30 to 18:30
      (ends after closing),
      when they submit the booking,
      then it is rejected with an error.

AC-19 Given a user books an appointment on a Tuesday from 09:00 to 10:00
      (within hours),
      then the booking succeeds.

NON-GOAL  No user accounts / login (v1)
NON-GOAL  No booking buffer/gap enforcement between appointments (v1)
[NEEDS CLARIFICATION]  What is the minimum/maximum number of attendees allowed per booking?
