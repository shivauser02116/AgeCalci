"""
age_logic.py - Pure age-calculation logic with no I/O.

Both app.py (Streamlit) and cli.py import from here.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------


class InvalidDOBError(Exception):
    """Raised when a date-of-birth string or date value fails validation."""


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class AgeResult:
    """Holds every computed field for a date-of-birth."""

    years: int
    months: int
    days: int
    total_days: int
    next_birthday: date
    days_until_next_birthday: int
    weekday_of_birth: str


# ---------------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------------


def calculate_age(dob: date, today: date | None = None) -> AgeResult:
    """Return an AgeResult for dob relative to today.

    Args:
        dob:   The date of birth.
        today: Reference date (injected for deterministic tests).
               Defaults to date.today() when None.

    Algorithm
    ---------
    1. Compute raw deltas in years, months, and days.
    2. If delta_days < 0:
       a. Determine the previous month relative to today (the borrow month).
       b. Add days_in_borrow_month to delta_days.
       c. Add max(0, dob.day - days_in_borrow_month) to delta_days.
          This correction handles month-end DOBs (e.g. Jan 31) where
          dob.day exceeds the days in the borrow month.
       d. Decrement delta_months by 1.
    3. If delta_months < 0: add 12, decrement delta_years.
    4. No approximations (no 30-day or 365-day shortcuts).
    """
    if today is None:
        today = date.today()

    delta_days = today.day - dob.day
    delta_months = today.month - dob.month
    delta_years = today.year - dob.year

    if delta_days < 0:
        borrow_month = today.month - 1 if today.month > 1 else 12
        borrow_year = today.year if today.month > 1 else today.year - 1
        days_in_borrow_month = calendar.monthrange(borrow_year, borrow_month)[1]
        delta_days += days_in_borrow_month + max(0, dob.day - days_in_borrow_month)
        delta_months -= 1

    if delta_months < 0:
        delta_months += 12
        delta_years -= 1

    total_days = (today - dob).days
    next_bday = _next_birthday(dob, today)
    days_until = (next_bday - today).days
    weekday = dob.strftime("%A")

    return AgeResult(
        years=delta_years,
        months=delta_months,
        days=delta_days,
        total_days=total_days,
        next_birthday=next_bday,
        days_until_next_birthday=days_until,
        weekday_of_birth=weekday,
    )


# ---------------------------------------------------------------------------
# Next-birthday helpers
# ---------------------------------------------------------------------------


def _next_birthday(dob: date, today: date) -> date:
    """Return the next occurrence of dob's anniversary on or after today.

    Feb-29 rule: When dob is Feb 29 and the target year is not a leap year,
    the anniversary is treated as Mar 1 (not Feb 28).
    """
    candidate = _safe_anniversary(dob, today.year)
    if candidate < today:
        candidate = _safe_anniversary(dob, today.year + 1)
    return candidate


def _safe_anniversary(dob: date, year: int) -> date:
    """Return the anniversary of dob in year, applying the Feb-29 rule.

    Args:
        dob:  The original date of birth.
        year: Target calendar year.

    Returns:
        The anniversary date, using Mar 1 when dob is Feb 29 in a non-leap year.
    """
    if dob.month == 2 and dob.day == 29:
        return date(year, 2, 29) if calendar.isleap(year) else date(year, 3, 1)
    return date(year, dob.month, dob.day)


# ---------------------------------------------------------------------------
# Validation / parsing
# ---------------------------------------------------------------------------


def parse_dob(text: str) -> date:
    """Parse text into a date, accepting DD-MM-YYYY and YYYY-MM-DD.

    Args:
        text: Raw date string supplied by the user.

    Returns:
        A validated date object.

    Raises:
        InvalidDOBError: With a user-friendly message on any validation failure.
    """
    text = text.strip()
    parsed: date | None = None

    if _looks_like(text, day_first=True):
        parsed = _try_parse(text, "%d-%m-%Y")
    elif _looks_like(text, day_first=False):
        parsed = _try_parse(text, "%Y-%m-%d")

    if parsed is None:
        raise InvalidDOBError(
            f"'{text}' could not be parsed. "
            "Date must be in DD-MM-YYYY or YYYY-MM-DD format."
        )

    _validate_date(parsed)
    return parsed


def _looks_like(text: str, *, day_first: bool) -> bool:
    """Quick structural check before attempting strptime.

    Args:
        text:      The raw input string.
        day_first: True => expect DD-MM-YYYY; False => expect YYYY-MM-DD.
    """
    parts = text.split("-")
    if len(parts) != 3:
        return False
    a, b, c = parts
    if day_first:
        return len(a) == 2 and len(b) == 2 and len(c) == 4
    return len(a) == 4 and len(b) == 2 and len(c) == 2


def _try_parse(text: str, fmt: str) -> date | None:
    """Attempt strptime with fmt; return None on any error.

    strptime rejects impossible dates (e.g. 31-02) with ValueError,
    so no separate calendar-validity check is needed.
    """
    from datetime import datetime
    try:
        return datetime.strptime(text, fmt).date()
    except ValueError:
        return None


def _validate_date(d: date) -> None:
    """Apply business-rule checks on an already-parsed date.

    Raises:
        InvalidDOBError: When d is before 1900 or after today.
    """
    if d.year < 1900:
        raise InvalidDOBError(
            f"Year {d.year} is too far in the past. "
            "Only years 1900 and later are supported."
        )
    today = date.today()
    if d > today:
        raise InvalidDOBError(
            "Date of birth cannot be in the future. "
            f"Today is {today.strftime('%d %b %Y')}."
        )
