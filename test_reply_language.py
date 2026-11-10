"""Tests for brain.handle() with force_lang and force_intent.

Checks that:
  - force_lang="te" produces Telugu characters (U+0C00-U+0C7F) for all 4 intents.
  - force_lang="hi" produces Devanagari characters (U+0900-U+097F) for all 4 intents.

Run:  python test_reply_language.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain import handle

EMP = "E1001"

# The 4 forced intents used by the Quick Demo buttons.
INTENTS = [
    ("leave_balance",  {"intent": "leave_balance"}),
    ("payslip_date",   {"intent": "payslip_date"}),
    ("leave_request",  {"intent": "leave_request", "days": 2, "start": "tomorrow", "leave_type": "casual"}),
    ("holiday_list",   {"intent": "holiday_list"}),
]

TE_RANGE = ("\u0c00", "\u0c7f")  # Telugu Unicode block
HI_RANGE = ("\u0900", "\u097f")  # Devanagari Unicode block


def _has_script(text: str, lo: str, hi: str) -> bool:
    return any(lo <= ch <= hi for ch in text)


def run_tests():
    passed = 0
    failed = 0
    print(f"\n{'─'*72}")
    print(f"  {'TEST':<44} {'LANG':<6} {'PASS?'}")
    print(f"{'─'*72}")

    for intent_name, intent_dict in INTENTS:
        for lang, (lo, hi), script_name in [
            ("te", TE_RANGE, "Telugu"),
            ("hi", HI_RANGE, "Devanagari"),
        ]:
            result = handle(
                EMP,
                text="",                    # text is irrelevant when force_intent is set
                detected_lang=None,
                force_intent=intent_dict,
                force_lang=lang,
            )
            reply = result["reply"]
            ok = _has_script(reply, lo, hi)
            status = "✅ PASS" if ok else f"❌ FAIL — reply: {reply[:60]!r}"
            desc = f"{intent_name} · {script_name}"
            print(f"  {desc:<44} {lang:<6} {status}")
            if ok:
                passed += 1
            else:
                failed += 1

    print(f"{'─'*72}")
    print(f"  {passed}/{passed+failed} passed", "🎉" if failed == 0 else "⚠️  fix the failures above")
    print(f"{'─'*72}\n")
    return failed


if __name__ == "__main__":
    failures = run_tests()
    sys.exit(failures)

