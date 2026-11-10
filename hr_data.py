"""Mock HR data standing in for Oracle Fusion HCM (swap with REST calls later).

Real-world mapping:
  leave balance  -> HCM REST  /absences  (accrual balances)
  payslip date   -> HCM REST  /payslips  (payment date)
  leave request  -> HCM REST  POST /absences  (starts an approval workflow)
  holiday list   -> HCM REST  /publicHolidays
"""
from datetime import date, timedelta

EMPLOYEES = {
    "E1001": {"name": "Ravi Kumar", "leave": {"casual": 7, "sick": 4, "earned": 12},
              "payslip_date": date(2026, 11, 30), "net_pay": 58200},
    "E1002": {"name": "Priya Sharma", "leave": {"casual": 3, "sick": 6, "earned": 9},
              "payslip_date": date(2026, 11, 30), "net_pay": 72450},
    "E1003": {"name": "Anil Reddy", "leave": {"casual": 10, "sick": 2, "earned": 15},
              "payslip_date": date(2026, 11, 30), "net_pay": 49800},
}

# Source: Central Govt holiday lists 2026 and 2027; Eid dates may shift by one day with moon sighting.
HOLIDAYS = [
    # ── 2026 ──────────────────────────────────────────────────────────────────
    {"date": date(2026,  1, 26), "name_en": "Republic Day",              "name_hi": "गणतंत्र दिवस",              "name_te": "గణతంత్ర దినోత్సవం",      "restricted": False},
    {"date": date(2026,  3,  4), "name_en": "Holi",                     "name_hi": "होली",                      "name_te": "హోలీ",                   "restricted": False},
    {"date": date(2026,  3, 21), "name_en": "Id-ul-Fitr",               "name_hi": "ईद-उल-फितर",                "name_te": "ఈద్-ఉల్-ఫితర్",          "restricted": False},
    {"date": date(2026,  4,  3), "name_en": "Good Friday",              "name_hi": "गुड फ्राइडे",               "name_te": "గుడ్ ఫ్రైడే",             "restricted": False},
    {"date": date(2026,  5, 27), "name_en": "Id-ul-Zuha (Bakrid)",      "name_hi": "ईद-उल-ज़ुहा (बकरीद)",       "name_te": "బక్రీద్",                 "restricted": False},
    {"date": date(2026,  6, 26), "name_en": "Muharram",                 "name_hi": "मुहर्रम",                   "name_te": "మొహర్రం",                 "restricted": False},
    {"date": date(2026,  8, 15), "name_en": "Independence Day",         "name_hi": "स्वतंत्रता दिवस",           "name_te": "స్వాతంత్ర్య దినోత్సవం",   "restricted": False},
    {"date": date(2026,  8, 26), "name_en": "Id-e-Milad",               "name_hi": "ईद-ए-मिलाद",               "name_te": "మిలాద్-ఉన్-నబీ",          "restricted": False},
    {"date": date(2026,  9,  4), "name_en": "Janmashtami",              "name_hi": "जन्माष्टमी",                "name_te": "జన్మాష్టమి",               "restricted": False},
    {"date": date(2026, 10,  2), "name_en": "Gandhi Jayanti",           "name_hi": "गांधी जयंती",               "name_te": "గాంధీ జయంతి",             "restricted": False},
    {"date": date(2026, 10, 20), "name_en": "Dussehra",                 "name_hi": "दशहरा",                     "name_te": "దసరా",                    "restricted": False},
    {"date": date(2026, 11,  8), "name_en": "Diwali",                   "name_hi": "दिवाली",                    "name_te": "దీపావళి",                  "restricted": False},
    {"date": date(2026, 11,  9), "name_en": "Govardhan Puja",           "name_hi": "गोवर्धन पूजा",              "name_te": "గోవర్ధన పూజ",             "restricted": True},
    {"date": date(2026, 11, 11), "name_en": "Bhai Dooj",                "name_hi": "भाई दूज",                   "name_te": "భాయ్ దూజ్",               "restricted": True},
    {"date": date(2026, 11, 24), "name_en": "Guru Nanak Jayanti",       "name_hi": "गुरु नानक जयंती",           "name_te": "గురునానక్ జయంతి",          "restricted": False},
    {"date": date(2026, 12, 25), "name_en": "Christmas",                "name_hi": "क्रिसमस",                   "name_te": "క్రిస్మస్",                "restricted": False},
    # ── 2027 ──────────────────────────────────────────────────────────────────
    {"date": date(2027,  1, 26), "name_en": "Republic Day",             "name_hi": "गणतंत्र दिवस",              "name_te": "గణతంత్ర దినోత్సవం",      "restricted": False},
    {"date": date(2027,  3, 10), "name_en": "Id-ul-Fitr",              "name_hi": "ईद-उल-फितर",                "name_te": "ఈద్-ఉల్-ఫితర్",          "restricted": False},
    {"date": date(2027,  3, 23), "name_en": "Holi",                    "name_hi": "होली",                      "name_te": "హోలీ",                   "restricted": False},
    {"date": date(2027,  3, 26), "name_en": "Good Friday",             "name_hi": "गुड फ्राइडे",               "name_te": "గుడ్ ఫ్రైడే",             "restricted": False},
    {"date": date(2027,  4, 15), "name_en": "Ram Navami",              "name_hi": "राम नवमी",                  "name_te": "శ్రీరామ నవమి",             "restricted": False},
    {"date": date(2027,  4, 19), "name_en": "Mahavir Jayanti",         "name_hi": "महावीर जयंती",              "name_te": "మహావీర్ జయంతి",           "restricted": False},
    {"date": date(2027,  5, 17), "name_en": "Id-ul-Zuha (Bakrid)",     "name_hi": "ईद-उल-ज़ुहा (बकरीद)",       "name_te": "బక్రీద్",                 "restricted": False},
    {"date": date(2027,  5, 20), "name_en": "Buddha Purnima",          "name_hi": "बुद्ध पूर्णिमा",            "name_te": "బుద్ధ పూర్ణిమ",           "restricted": False},
    {"date": date(2027,  6, 16), "name_en": "Muharram",                "name_hi": "मुहर्रम",                   "name_te": "మొహర్రం",                 "restricted": False},
    {"date": date(2027,  8, 15), "name_en": "Independence Day",        "name_hi": "स्वतंत्रता दिवस",           "name_te": "స్వాతంత్ర్య దినోత్సవం",   "restricted": False},
    {"date": date(2027,  8, 15), "name_en": "Id-e-Milad",              "name_hi": "ईद-ए-मिलाद",               "name_te": "మిలాద్-ఉన్-నబీ",          "restricted": False},
    {"date": date(2027,  8, 25), "name_en": "Janmashtami",             "name_hi": "जन्माष्टमी",                "name_te": "జన్మాష్టమి",               "restricted": False},
    {"date": date(2027, 10,  2), "name_en": "Gandhi Jayanti",          "name_hi": "गांधी जयंती",               "name_te": "గాంధీ జయంతి",             "restricted": False},
    {"date": date(2027, 10,  9), "name_en": "Dussehra",                "name_hi": "दशहरा",                     "name_te": "దసరా",                    "restricted": False},
    {"date": date(2027, 10, 29), "name_en": "Diwali",                  "name_hi": "दिवाली",                    "name_te": "దీపావళి",                  "restricted": False},
    {"date": date(2027, 11, 14), "name_en": "Guru Nanak Jayanti",      "name_hi": "गुरु नानक जयंती",           "name_te": "గురునానక్ జయంతి",          "restricted": False},
    {"date": date(2027, 12, 25), "name_en": "Christmas",               "name_hi": "क्रिसमस",                   "name_te": "క్రిస్మస్",                "restricted": False},
]


def leave_balance(emp_id: str) -> dict:
    return EMPLOYEES[emp_id]["leave"]


def payslip_info(emp_id: str) -> dict:
    e = EMPLOYEES[emp_id]
    return {"date": e["payslip_date"], "net_pay": e["net_pay"]}


def upcoming_holidays(n: int = 3) -> list[dict]:
    today = date.today()
    future = sorted(
        [h for h in HOLIDAYS if h["date"] > today],  # strictly after today
        key=lambda h: h["date"]
    )
    return future[:n]


def create_leave_request(emp_id: str, days: int, start: date, kind: str = "casual") -> dict:
    """Validate against balance and return a request record (not persisted)."""
    balance = EMPLOYEES[emp_id]["leave"].get(kind, 0)
    end = start + timedelta(days=days - 1)
    ok = days <= balance
    return {
        "employee": emp_id, "type": kind, "days": days,
        "start": start.isoformat(), "end": end.isoformat(),
        "status": "Submitted for manager approval" if ok else "Rejected: insufficient balance",
        "ok": ok, "balance": balance,
    }
