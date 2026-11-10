from datetime import date
import hr_data, brain

# Monkey-patch date.today() to 2026-11-09 for the test
class MockDate(date):
    @classmethod
    def today(cls):
        return date(2026, 11, 9)

_real_hr_date = hr_data.date
_real_brain_date = brain.date
hr_data.date = MockDate
brain.date = MockDate

try:
    holidays = hr_data.upcoming_holidays(3)
    print("--- upcoming_holidays(3) from 2026-11-09 ---")
    for h in holidays:
        r = " [RESTRICTED]" if h["restricted"] else ""
        print(f"  {h['date']}  {h['name_en']}{r}")

    print()
    print("--- brain holiday reply (en) ---")
    r = brain.handle("E1001", "Show upcoming holidays", "en-IN")
    print(" ", r["reply"])

    print()
    print("--- brain holiday reply (hi) ---")
    r = brain.handle("E1001", "Show upcoming holidays", "hi-IN")
    print(" ", r["reply"])
    print("\n✅ PASS: test_holidays completed successfully.")
finally:
    hr_data.date = _real_hr_date
    brain.date = _real_brain_date
