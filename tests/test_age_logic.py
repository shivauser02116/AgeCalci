"""
tests/test_age_logic.py -- Deterministic pytest suite for age_logic.py.

Every test injects today= explicitly so the wall clock is never consulted.
Expected values are pre-computed by hand and annotated inline.
"""

from __future__ import annotations

from datetime import date

import pytest

from age_logic import AgeResult, InvalidDOBError, calculate_age, parse_dob

WEEKDAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}


def age(dob: date, today: date) -> AgeResult:
    """Thin wrapper so tests stay concise."""
    return calculate_age(dob=dob, today=today)


# ===========================================================================
# 1. Normal case
# ===========================================================================

def test_normal_case():
    """Born 2000-06-15, today 2026-11-18 => 26 y, 5 m, 3 d.
    Raw: delta_days=18-15=3, delta_months=11-6=5, delta_years=26. No borrowing.
    """
    r = age(date(2000, 6, 15), date(2026, 11, 18))
    assert r.years == 26
    assert r.months == 5
    assert r.days == 3


# ===========================================================================
# 2. Birthday today
# ===========================================================================

def test_birthday_today():
    """When today IS the birthday month/day, months=0, days=0, days_until=0."""
    r = age(date(1990, 7, 4), date(2025, 7, 4))
    assert r.years == 35
    assert r.months == 0
    assert r.days == 0
    assert r.days_until_next_birthday == 0


# ===========================================================================
# 3. Birthday tomorrow
# ===========================================================================

def test_birthday_tomorrow():
    """One day before birthday -- days_until_next_birthday == 1."""
    r = age(date(1990, 7, 4), date(2025, 7, 3))
    assert r.days_until_next_birthday == 1


# ===========================================================================
# 4. Born yesterday
# ===========================================================================

def test_born_yesterday():
    """Born one day ago => 0 y, 0 m, 1 d."""
    r = age(date(2026, 11, 17), date(2026, 11, 18))
    assert r.years == 0
    assert r.months == 0
    assert r.days == 1


# ===========================================================================
# 5. Month-end borrowing -- non-leap year (Feb = 28 days)
# ===========================================================================

def test_jan31_to_mar1_non_leap():
    """Born Jan 31, today Mar 1 of a non-leap year (2025).

    delta_days = 1-31 = -30
    borrow Feb 2025 (28 d): -30 + 28 + max(0, 31-28) = -30+31 = 1
    delta_months = 3-1-1 = 1
    delta_years = 25
    Expected: 25 y, 1 m, 1 d.
    """
    r = age(date(2000, 1, 31), date(2025, 3, 1))
    assert r.years == 25
    assert r.months == 1
    assert r.days == 1


# ===========================================================================
# 6. Month-end borrowing -- leap year (Feb = 29 days)
# ===========================================================================

def test_jan31_to_mar1_leap():
    """Born Jan 31, today Mar 1 of a leap year (2024).

    delta_days = 1-31 = -30
    borrow Feb 2024 (29 d): -30 + 29 + max(0, 31-29) = -30+31 = 1
    delta_months = 3-1-1 = 1
    delta_years = 24
    Expected: 24 y, 1 m, 1 d.
    """
    r = age(date(2000, 1, 31), date(2024, 3, 1))
    assert r.years == 24
    assert r.months == 1
    assert r.days == 1


# ===========================================================================
# 7. Born Feb 29 -- today is Feb 28 in a non-leap year
# ===========================================================================

def test_feb29_today_feb28_non_leap():
    """Feb-29 DOB; today is Feb 28, 2025 (non-leap) -- birthday has not arrived.

    Last birthday: Feb 29, 2024 (leap).
    delta_days = 28-29 = -1; borrow Jan 2025 (31 d): -1+31+0 = 30
    delta_months = 2-2-1 = -1 => +12 => 11; delta_years = 25-1 = 24
    Expected: 24 y, 11 m, 30 d.
    """
    r = age(date(2000, 2, 29), date(2025, 2, 28))
    assert r.years == 24
    assert r.months == 11
    assert r.days == 30


# ===========================================================================
# 8. Born Feb 29 -- today is Mar 1 in a non-leap year
# ===========================================================================

def test_feb29_today_mar1_non_leap():
    """Feb-29 DOB; today is Mar 1, 2025 (non-leap).

    delta_days = 1-29 = -28; borrow Feb 2025 (28 d): -28+28+max(0,29-28)=1
    delta_months = 3-2-1 = 0; delta_years = 25
    Expected: 25 y, 0 m, 1 d.
    next_birthday = Mar 1, 2026 (Feb-29 rule).
    """
    r = age(date(2000, 2, 29), date(2025, 3, 1))
    assert r.years == 25
    assert r.months == 0
    assert r.days == 1
    assert r.next_birthday == date(2025, 3, 1)  # today IS birthday via Feb-29 rule
    assert r.days_until_next_birthday == 0


# ===========================================================================
# 9. Born Feb 29 -- today is Feb 29 in a leap year (exact hit)
# ===========================================================================

def test_feb29_today_feb29_leap():
    """Feb-29 DOB; today is Feb 29, 2024 -- exact birthday, days_until=0."""
    r = age(date(2000, 2, 29), date(2024, 2, 29))
    assert r.years == 24
    assert r.months == 0
    assert r.days == 0
    assert r.days_until_next_birthday == 0
    assert r.next_birthday == date(2024, 2, 29)


# ===========================================================================
# 10. Born Dec 31 -- today is Jan 1
# ===========================================================================

def test_dec31_to_jan1():
    """Born Dec 31, today Jan 1 of the next year => 0 y, 0 m, 1 d.

    delta_days = 1-31 = -30; borrow Dec 2000 (31 d): -30+31+0 = 1
    delta_months = 1-12-1 = -12 => +12 => 0; delta_years = 1-1 = 0
    Expected: 0 y, 0 m, 1 d.
    """
    r = age(date(2000, 12, 31), date(2001, 1, 1))
    assert r.years == 0
    assert r.months == 0
    assert r.days == 1


# ===========================================================================
# 11. Future date rejected
# ===========================================================================

def test_future_date_rejected():
    """parse_dob raises InvalidDOBError for a date in the future."""
    with pytest.raises(InvalidDOBError, match="future"):
        parse_dob("01-01-2099")


# ===========================================================================
# 12. Impossible date: Feb 31 rejected
# ===========================================================================

def test_impossible_date_feb31():
    """parse_dob raises InvalidDOBError for the non-existent Feb 31."""
    with pytest.raises(InvalidDOBError):
        parse_dob("31-02-2001")


# ===========================================================================
# 13. Garbage text rejected
# ===========================================================================

def test_garbage_text_rejected():
    """parse_dob raises InvalidDOBError for unrecognised text."""
    with pytest.raises(InvalidDOBError):
        parse_dob("not-a-date")


# ===========================================================================
# 14. Year before 1900 rejected
# ===========================================================================

def test_year_before_1900_rejected():
    """parse_dob raises InvalidDOBError for year 1899."""
    with pytest.raises(InvalidDOBError, match="1900"):
        parse_dob("01-01-1899")


# ===========================================================================
# 15. Feb 29 in a non-leap year rejected
# ===========================================================================

def test_feb29_non_leap_rejected():
    """parse_dob raises InvalidDOBError for Feb 29, 2023 (non-leap)."""
    with pytest.raises(InvalidDOBError):
        parse_dob("29-02-2023")


# ===========================================================================
# 16. Both accepted date formats
# ===========================================================================

def test_both_formats_accepted():
    """DD-MM-YYYY and YYYY-MM-DD should both parse to the same date."""
    d1 = parse_dob("15-06-2000")
    d2 = parse_dob("2000-06-15")
    assert d1 == d2 == date(2000, 6, 15)


# ===========================================================================
# 17. total_days cross-check
# ===========================================================================

def test_total_days_matches_timedelta():
    """total_days must equal (today - dob).days."""
    dob = date(1985, 3, 22)
    today = date(2026, 11, 18)
    r = age(dob, today)
    assert r.total_days == (today - dob).days


# ===========================================================================
# 18. weekday_of_birth is a valid weekday name
# ===========================================================================

def test_weekday_of_birth_valid():
    """weekday_of_birth must be one of the seven weekday names."""
    r = age(date(2000, 6, 15), date(2026, 11, 18))
    assert r.weekday_of_birth in WEEKDAYS
    assert r.weekday_of_birth == "Thursday"  # 2000-06-15 was a Thursday


# ===========================================================================
# 19. next_birthday is always >= today
# ===========================================================================

def test_next_birthday_not_in_past():
    """next_birthday must be on or after today in all cases."""
    cases = [
        (date(2000, 6, 15), date(2026, 11, 18)),
        (date(2000, 2, 29), date(2025, 2, 28)),
        (date(1990, 7, 4),  date(2025, 7, 4)),
        (date(1990, 7, 4),  date(2025, 7, 3)),
        (date(2000, 12, 31), date(2026, 1, 1)),
    ]
    for dob, today in cases:
        r = age(dob, today)
        assert r.next_birthday >= today, (
            f"next_birthday {r.next_birthday} < today {today} for dob={dob}"
        )


# ===========================================================================
# 20. days_until_next_birthday bounds
# ===========================================================================

def test_days_until_next_birthday_bounds():
    """days_until_next_birthday must be between 0 and 366 inclusive."""
    cases = [
        (date(2000, 6, 15), date(2026, 11, 18)),
        (date(2000, 2, 29), date(2025, 2, 28)),
        (date(1990, 7, 4),  date(2025, 7, 4)),
        (date(1990, 7, 4),  date(2025, 7, 3)),
        (date(2000, 12, 31), date(2026, 1, 1)),
    ]
    for dob, today in cases:
        r = age(dob, today)
        assert 0 <= r.days_until_next_birthday <= 366, (
            f"days_until={r.days_until_next_birthday} out of range "
            f"for dob={dob}, today={today}"
        )
