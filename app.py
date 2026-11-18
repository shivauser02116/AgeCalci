"""
app.py — Streamlit GUI for the Age Calculator.

Calls calculate_age() and parse_dob() from age_logic.py.
No age logic lives here.
"""

from __future__ import annotations

from datetime import date

import streamlit as st

from age_logic import AgeResult, InvalidDOBError, calculate_age

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Age Calculator",
    page_icon="🎂",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🎂 Age Calculator")
st.caption(
    "Enter your date of birth to find out your exact age in years, months, "
    "and days — plus a few fun extras."
)

st.divider()

# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

today_real = date.today()

col_dob, col_asof = st.columns(2)

with col_dob:
    dob_input: date = st.date_input(
        "📅 Date of Birth",
        value=date(1990, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=today_real,
        format="DD/MM/YYYY",
        help="Your date of birth (between 01 Jan 1900 and today).",
    )

with col_asof:
    use_custom_asof = st.checkbox("Calculate age as of a specific date", value=False)
    if use_custom_asof:
        asof_input: date = st.date_input(
            "📆 As-of Date",
            value=today_real,
            min_value=date(1900, 1, 1),
            max_value=today_real,
            format="DD/MM/YYYY",
            help="Calculate what the age would be on this date.",
        )
    else:
        asof_input = today_real

st.divider()

# ---------------------------------------------------------------------------
# Calculate and display
# ---------------------------------------------------------------------------

calculate_clicked = st.button("Calculate Age", type="primary", use_container_width=True)

if calculate_clicked or True:  # auto-calculate on every render
    try:
        # Validate that dob is not after asof (extra guard beyond the widget)
        if dob_input > asof_input:
            st.error(
                "Date of birth cannot be after the 'as-of' date. "
                "Please check your inputs."
            )
        else:
            result: AgeResult = calculate_age(dob=dob_input, today=asof_input)

            # --- Primary metrics ---
            st.subheader("Your Age")
            m1, m2, m3 = st.columns(3)
            m1.metric("🗓️ Years", result.years)
            m2.metric("📅 Months", result.months)
            m3.metric("🌙 Days", result.days)

            st.divider()

            # --- Extra info ---
            st.subheader("Fun Facts")

            info_col1, info_col2 = st.columns(2)

            with info_col1:
                st.info(f"**Total days lived:** {result.total_days:,}")
                st.info(f"**Born on a:** {result.weekday_of_birth}")

            with info_col2:
                if result.days_until_next_birthday == 0:
                    st.success("🎉 **Happy Birthday!** Your birthday is today!")
                elif result.days_until_next_birthday == 1:
                    st.warning("🎁 Your birthday is **tomorrow**!")
                else:
                    st.info(
                        f"**Next birthday:** {result.next_birthday.strftime('%d %b %Y')} "
                        f"({result.days_until_next_birthday} days away)"
                    )

    except InvalidDOBError as exc:
        st.error(f"⚠️ {exc}")
    except Exception as exc:  # safety net — never show a traceback
        st.error(f"⚠️ An unexpected error occurred: {exc}")
