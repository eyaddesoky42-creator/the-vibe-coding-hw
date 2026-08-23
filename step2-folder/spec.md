FR-1  A user can book an appointment by providing:
      - a date
      - a start time
      - an end time
      - their name
      - their email
      - number of attendees (optional — defaults to 1 if not provided)

      The date must be a real calendar date (e.g. "2026-06-31" is invalid,
      since June only has 30 days) and must fall within 1 year from today.
      Dates further than 1 year out, or dates in the past, are rejected
      with an error.

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
AC-20 Given today's date is 2026-08-24,
      when a user tries to book an appointment on 2026-06-31 (not a real date),
      then the booking is rejected with an error.

AC-21 Given today's date is 2026-08-24,
      when a user tries to book an appointment on 2027-09-01
      (more than 1 year away),
      then the booking is rejected with an error.

AC-22 Given today's date is 2026-08-24,
      when a user books an appointment on 2027-08-01 (within 1 year),
      then the booking succeeds (subject to the other FRs, e.g. FR-4's
      2-hour minimum and FR-5's business hours).      

FR-2  Booking a date and start/end time that overlaps with an existing appointment
      on the same date is rejected with an error. This includes exact
      slots and any partial overlap. Back-to-back bookings (one ending exactly
      when another starts) are NOT a conflict and are allowed.

AC-5  Given an appointment scheduled on 2026-12-01 from 08:00 to 09:00,
      when a user tries to book 2026-12-01 from 08:00 to 09:00 (exact match),
      then the booking is rejected with an error.

AC-6  Given an appointment scheduled on 2026-12-01 from 08:00 to 09:00,
      when a user tries to book 2026-12-01 from 08:30 to 09:30 (partial overlap),
      then the booking is rejected with an error.

AC-7  Given an appointment scheduled on 2026-12-01 from 08:00 to 09:00,
      when a user books 2026-12-05 from 10:00 to 11:00 (different day entirely),
      then the booking succeeds.

AC-8  Given an appointment scheduled on 2026-12-01 from 08:00 to 09:00,
      when a user books 2026-12-01 from 09:00 to 11:00 (back-to-back, no overlap),
      then the booking succeeds.

FR-3  A user (identified by email) cannot have more than one appointment
      on the same date. Email matching is case-insensitive and ignores
      leading/trailing whitespace — "[email protected]" and " a@x.com "
      are treated as the same person. A booking attempt with an email
      that already has an appointment on that date is rejected with an
      error.

AC-9  Given [email protected] has an appointment on 2026-12-01,
      when [email protected] tries to book an appointment on 2026-12-02,
      then the booking succeeds.
      
AC-10  Given [email protected] has an appointment on 2026-12-01,
      when [email protected] tries to book an appointment on 2026-12-01,
      then the booking is rejected with an error

AC-11 Given [email protected] has an appointment on 2026-12-01,
      when [email protected] tries to book an appointment on 2026-12-01
      (different email, no conflict),
      then the booking succeeds.

AC-23 Given "[email protected]" has an appointment on 2026-12-01,
      when " ALICE@X.COM " (different case, extra spaces) tries to book
      an appointment on 2026-12-01,
      then the booking is rejected with an error (treated as the same
      person).


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
      when a user books an appointment starting at 2026-09-02 10:00
      (next day, well past the 2-hour minimum),
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

NON-GOAL  We're not building real protection against two people booking
          the exact same slot at the exact same second. This is a small,
          single-user app, so that risk is basically theoretical — not
          worth the extra complexity for v1.

[NEEDS CLARIFICATION]  What is the minimum/maximum number of attendees allowed per booking?

[NEEDS CLARIFICATION]  Does the email need to be validated as a real email format (e.g. must contain "@"), or is any non-empty string accepted?

[NEEDS CLARIFICATION]  Can appointments start at any minute (e.g. 10:07), or only at fixed increments (e.g. every 15 or 30 minutes)?

[NEEDS CLARIFICATION]  Is a booking starting exactly at 08:00 or ending
exactly at 18:00 considered within business hours (inclusive), or must
it be strictly between them (exclusive)?

[NEEDS CLARIFICATION]  Is there a minimum or maximum length for an
appointment? Should a booking where the end time is before or equal to
the start time (zero-length or reversed) be explicitly rejected?