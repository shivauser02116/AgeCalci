# 🎂 Age Calculator

A clean, tested, deployable Python app that calculates your **exact age** in years, months, and days from a date of birth.

Available as both a **Streamlit web app** and an **interactive CLI**.

> **Live demo:** *(deploy URL — fill in after Streamlit Community Cloud deployment)*

---

## Features

- Exact age: years, months, days (no 30-day or 365-day approximations)
- Total days lived
- Day of the week you were born
- Countdown to your next birthday
- Optional "calculate age as of" any past date
- Accepts both `DD-MM-YYYY` and `YYYY-MM-DD` input formats
- Robust validation with clear, user-friendly error messages (no tracebacks ever shown)

---

## Project Structure

```
age_calculator/
├── age_logic.py              # Pure functions — all logic lives here
├── app.py                    # Streamlit GUI
├── cli.py                    # Interactive CLI
├── tests/
│   └── test_age_logic.py     # 20 pytest test cases
├── conftest.py               # pytest sys.path setup
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Setup

### Prerequisites

- Python 3.10 or later
- pip

### Install dependencies

```bash
cd age_calculator
pip install -r requirements.txt
```

---

## Running the app

### Streamlit GUI

```bash
streamlit run app.py
```

The app opens at [http://localhost:8501](http://localhost:8501).

### Interactive CLI

```bash
python cli.py
```

```
╔══════════════════════════════════════════╗
║          🎂  AGE CALCULATOR  🎂           ║
╚══════════════════════════════════════════╝
  Accepted formats: DD-MM-YYYY | YYYY-MM-DD

  Enter date of birth: 15-06-2000
  ...
  Calculate another age? (y/n):
```

---

## Running the tests

```bash
pytest tests/ -v
```

Expected output: **20 tests passed**.

---

## Algorithm Notes

### Exact borrowing (no approximations)

The algorithm subtracts year, month, and day fields directly.  When the day
field goes negative it borrows from the **previous calendar month** using
`calendar.monthrange` for the exact day count.

A month-end correction handles dates like January 31:

```
Born Jan 31, today Mar 1 (non-leap, Feb = 28 days):
  Δdays = 1 − 31 = −30
  borrow Feb (28 d) + correction max(0, 31−28)=3  →  −30+31 = 1 day
  Δmonths = 3 − 1 − 1 = 1
  → 1 month, 1 day  ✓
```

### Feb 29 birthdays

When a person is born on **February 29** and their birthday falls in a
non-leap year, the app treats the anniversary as **March 1** for the
*next-birthday* calculation.  This follows the "last day of the month"
convention used in several legal jurisdictions.

The age in years/months/days is computed from the raw date arithmetic and
is unaffected by this rule.

**Examples:**

| Today | next_birthday |
|---|---|
| Feb 28, 2025 (non-leap) | Mar 1, 2025 |
| Mar 1, 2025 (non-leap) | Mar 1, 2026 |
| Feb 29, 2024 (leap) | Feb 29, 2024 (today!) |

### Validation rules

| Input | Behaviour |
|---|---|
| `31-02-2001` | Rejected — impossible date |
| `29-02-2023` | Rejected — 2023 is not a leap year |
| `01-01-2099` | Rejected — future date |
| `01-01-1899` | Rejected — before year 1900 |
| Any non-date string | Rejected with format hint |

---

## Deployment to Streamlit Community Cloud

### 1. Push to GitHub

```bash
# In age_calculator/ (the repo root)
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Streamlit Community Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
2. Click **"New app"**.
3. Select your repository and branch (`main`).
4. Set **Main file path** to `app.py`.
5. Click **"Deploy"**.
6. Wait ~60 seconds for the first build to complete.
7. Copy the generated URL and paste it into the `README.md` live-demo line above.

> **Tip:** Streamlit Community Cloud reads `requirements.txt` automatically.
> No `Dockerfile` or `setup.py` is needed.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Core logic | Python 3.10+, `datetime`, `calendar` (stdlib only) |
| GUI | Streamlit |
| CLI | Python built-ins (`input`, `print`) |
| Tests | pytest |
| Deployment | Streamlit Community Cloud |
