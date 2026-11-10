"""8 intent-detection tests for brain.rule_intent().

Covers leave_balance, payslip_date, leave_request, holiday_list
in English, Hindi, Telugu and Hinglish.

Run:  python test_brain.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain import rule_intent

TESTS = [
    # (description, input_text, expected_intent)

    # ── leave_balance ─────────────────────────────────────────────────────────
    ("leave_balance · English",
     "How many leaves do I have left?",
     "leave_balance"),

    ("leave_balance · Hindi",
     "मेरी कितनी छुट्टियां बाकी हैं",
     "leave_balance"),

    # ── payslip_date ──────────────────────────────────────────────────────────
    ("payslip_date · Telugu",
     "నా జీతం ఎప్పుడు వస్తుంది",
     "payslip_date"),

    ("payslip_date · Hinglish",
     "Mera salary kab milega",
     "payslip_date"),

    # ── leave_request ─────────────────────────────────────────────────────────
    ("leave_request · English",
     "I need 3 days sick leave from tomorrow",
     "leave_request"),

    ("leave_request · Hinglish",
     "Kal ke liye 2 din ki chutti chahiye",
     "leave_request"),

    # ── holiday_list ──────────────────────────────────────────────────────────
    ("holiday_list · English",
     "Show upcoming holidays",
     "holiday_list"),

    ("holiday_list · Hindi",
     "त्योहार कब हैं",
     "holiday_list"),
]


def run_tests():
    passed = 0
    failed = 0
    print(f"\n{'─'*62}")
    print(f"  {'TEST':<38} {'EXPECTED':<16} {'GOT':<16}")
    print(f"{'─'*62}")
    for desc, text, expected in TESTS:
        got = rule_intent(text).get("intent")
        ok = got == expected
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {desc:<38} {expected:<16} {got:<16}  {status}")
        if ok:
            passed += 1
        else:
            failed += 1
    print(f"{'─'*62}")
    print(f"  {passed}/{len(TESTS)} passed", "🎉" if failed == 0 else "⚠️  fix the failures above")
    print(f"{'─'*62}\n")
    return failed


if __name__ == "__main__":
    failures = run_tests()
    sys.exit(failures)

