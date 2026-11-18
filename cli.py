"""
cli.py — Interactive command-line interface for the Age Calculator.

Calls parse_dob() and calculate_age() from age_logic.py.
No age logic lives here.
"""

from __future__ import annotations

from age_logic import AgeResult, InvalidDOBError, calculate_age, parse_dob

# ---------------------------------------------------------------------------
# Display helper
# ---------------------------------------------------------------------------


def display_result(result: AgeResult) -> None:
    """Print a formatted AgeResult to stdout."""
    print()
    print("=" * 44)
    print("  AGE RESULT")
    print("=" * 44)
    print(f"  Years  : {result.years}")
    print(f"  Months : {result.months}")
    print(f"  Days   : {result.days}")
    print("-" * 44)
    print(f"  Total days lived  : {result.total_days:,}")
    print(f"  Born on a         : {result.weekday_of_birth}")

    if result.days_until_next_birthday == 0:
        print("  🎉  Happy Birthday!")
    elif result.days_until_next_birthday == 1:
        print(
            f"  Next birthday     : {result.next_birthday.strftime('%d %b %Y')} "
            "(tomorrow!)"
        )
    else:
        print(
            f"  Next birthday     : {result.next_birthday.strftime('%d %b %Y')} "
            f"({result.days_until_next_birthday} days away)"
        )
    print("=" * 44)
    print()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the interactive Age Calculator CLI loop."""
    print()
    print("╔══════════════════════════════════════════╗")
    print("║          🎂  AGE CALCULATOR  🎂           ║")
    print("╚══════════════════════════════════════════╝")
    print("  Accepted formats: DD-MM-YYYY | YYYY-MM-DD")
    print()

    while True:
        raw = input("  Enter date of birth: ").strip()

        try:
            dob = parse_dob(raw)
        except InvalidDOBError as exc:
            print(f"\n  ⚠️  {exc}\n")
            continue  # re-prompt, do not exit

        result = calculate_age(dob)
        display_result(result)

        again = input("  Calculate another age? (y/n): ").strip().lower()
        print()
        if again != "y":
            print("  Goodbye! 👋")
            print()
            break


if __name__ == "__main__":
    main()
