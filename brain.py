"""Intent understanding + reply composition for the voice HR helpdesk.

Intent detection uses an LLM when one is configured (any OpenAI-compatible
server, e.g. Gnani Evon served with vLLM), and falls back to keyword rules
so the demo never breaks. Replies come from fixed templates in en / hi / te,
so numbers spoken back are always taken straight from the HR data.
"""
import json
import os
import re
from datetime import date, timedelta

import requests

import hr_data

INTENTS = ["leave_balance", "payslip_date", "leave_request", "holiday_list", "unknown"]

SYSTEM_PROMPT = """You are an HR helpdesk intent classifier for Indian employees.
The user's message may be English, Hindi, Telugu or mixed (Hinglish).
Return ONLY a JSON object: {"intent": one of ["leave_balance","payslip_date","leave_request","holiday_list","unknown"],
"days": integer or null, "start": "tomorrow" | "today" | "YYYY-MM-DD" | null, "leave_type": "casual"|"sick"|"earned"|null}.
leave_balance = asking how many leaves are left. payslip_date = asking about salary/payslip date.
leave_request = wants to apply for / take leave. holiday_list = asking about upcoming public/national/gazetted holidays."""

# ---- keyword fallback (English, Hindi, Telugu, common Hinglish) ----
KW_PAYSLIP = ["salary", "payslip", "pay slip", "payday", "वेतन", "सैलरी", "तनख्वाह", "पेस्लिप",
              "జీతం", "జీతము", "పేస్లిప్", "salary kab", "tankhwa"]
KW_HOLIDAY_LIST = ["holiday", "holidays", "public holiday", "national holiday",
                   "gazetted", "festival", "tyohar", "त्योहार", "सार्वजनिक अवकाश",
                   "పండుగ", "జాతీయ సెలవు", "upcoming holiday"]
KW_REQUEST = ["apply", "request", "need", "want", "take", "book", "चाहिए", "chahiye",
              "लेनी", "लेना", "आवेदन", "అప్లై", "కావాలి", "తీసుకోవాలి", "dena hai", "lena hai"]
KW_LEAVE = ["leave", "leaves", "balance", "छुट्टी", "छुट्टियां", "छुट्टियाँ", "సెలవు", "సెలవులు",
            "chutti", "chhutti"]
KW_TOMORROW = ["tomorrow", "कल", "రేపు", "kal", "repu"]
KW_SICK = ["sick", "ill", "fever", "बीमार", "అనారోగ్య", "bukhar"]

NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "ek": 1, "do": 2, "teen": 3,
             "char": 4, "paanch": 5, "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5, "పాంచ్": 5,
             "ఒకటి": 1, "రెండు": 2, "మూడు": 3, "నాలుగు": 4, "ఐదు": 5}


def _has(text: str, words: list[str]) -> bool:
    t = text.lower()
    return any(w in t for w in words)


def _days_from_text(text: str) -> int:
    m = re.search(r"\b(\d{1,2})\b", text)
    if m:
        return max(1, int(m.group(1)))
    for w, n in NUM_WORDS.items():
        if w in text.lower():
            return n
    return 1


def rule_intent(text: str) -> dict:
    if _has(text, KW_PAYSLIP):
        return {"intent": "payslip_date"}
    if _has(text, KW_HOLIDAY_LIST):
        return {"intent": "holiday_list"}
    if _has(text, KW_LEAVE) and _has(text, KW_REQUEST):
        return {"intent": "leave_request", "days": _days_from_text(text),
                "start": "tomorrow" if _has(text, KW_TOMORROW) else "today",
                "leave_type": "sick" if _has(text, KW_SICK) else "casual"}
    if _has(text, KW_LEAVE):
        return {"intent": "leave_balance"}
    return {"intent": "unknown"}


def llm_intent(text: str) -> dict | None:
    """Optional: OpenAI-compatible chat endpoint (e.g. vLLM serving Evon)."""
    base, model = os.environ.get("LLM_BASE_URL"), os.environ.get("LLM_MODEL")
    if not base or not model:
        return None
    headers = {"Content-Type": "application/json"}
    if os.environ.get("LLM_API_KEY"):
        headers["Authorization"] = f"Bearer {os.environ['LLM_API_KEY']}"
    try:
        r = requests.post(
            base.rstrip("/") + "/chat/completions", headers=headers, timeout=30,
            json={"model": model, "temperature": 0,
                  "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                               {"role": "user", "content": text}]})
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.S)
        data = json.loads(re.search(r"\{.*\}", content, re.S).group(0))
        return data if data.get("intent") in INTENTS else None
    except Exception:
        return None  # fall back to rules


def understand(text: str) -> tuple[dict, str]:
    """Returns (intent dict, source) where source is 'llm' or 'rules'."""
    parsed = llm_intent(text)
    if parsed:
        return parsed, "llm"
    return rule_intent(text), "rules"


# ---- language helpers ----
def lang_family(code: str | None) -> str:
    c = (code or "").lower()
    if c.startswith("te"):
        return "te"
    if c.startswith("hi") or "-hi-" in c or c.startswith("en-hi"):
        return "hi"
    return "en"


TTS_LANG = {"en": "en-IN", "hi": "hi-IN", "te": "te-IN"}

# Check the Gnani Voice Catalog (docs.gnani.ai) for Telugu voices.
TTS_VOICE = {
    "en": None,
    "hi": None,
    "te": None,
}

REPLIES = {
    "en": {
        "balance": "Hello {name}. You have {casual} casual, {sick} sick and {earned} earned leave days left.",
        "payslip": "Hello {name}. Your payslip will be available on {date}. Net pay is {net} rupees.",
        "req_ok": "Done {name}. I submitted {days} day {kind} leave from {start} for manager approval.",
        "req_fail": "Sorry {name}. You only have {bal} {kind} leave days left, so I could not submit {days} days.",
        "holidays": "Hello {name}. The next upcoming holidays are: {list}.",
        "unknown": "Sorry, I did not catch that. You can ask about leave balance, payslip date, upcoming holidays, or apply for leave.",
    },
    "hi": {
        "balance": "नमस्ते {name}। आपकी {casual} आकस्मिक, {sick} बीमारी और {earned} अर्जित छुट्टियाँ बाकी हैं।",
        "payslip": "नमस्ते {name}। आपकी पेस्लिप {date} को मिलेगी। नेट वेतन {net} रुपये है।",
        "req_ok": "हो गया {name}। मैंने {start} से {days} दिन की {kind} छुट्टी मैनेजर की मंज़ूरी के लिए भेज दी है।",
        "req_fail": "माफ़ कीजिए {name}। आपकी सिर्फ़ {bal} {kind} छुट्टियाँ बची हैं, इसलिए {days} दिन की अर्ज़ी नहीं भेज सका।",
        "holidays": "नमस्ते {name}। आने वाली छुट्टियाँ हैं: {list}।",
        "unknown": "माफ़ कीजिए, मैं समझ नहीं पाया। आप छुट्टी बैलेंस, पेस्लिप की तारीख़, त्योहारों की सूची पूछ सकते हैं या छुट्टी के लिए आवेदन कर सकते हैं।",
    },
    "te": {
        "balance": "నమస్కారం {name}. మీకు {casual} క్యాజువల్, {sick} సిక్ మరియు {earned} ఎర్న్డ్ సెలవులు మిగిలి ఉన్నాయి.",
        "payslip": "నమస్కారం {name}. మీ పేస్లిప్ {date} న అందుబాటులో ఉంటుంది. నికర జీతం {net} రూపాయలు.",
        "req_ok": "పూర్తైంది {name}. {start} నుండి {days} రోజుల {kind} సెలవు మేనేజర్ ఆమోదం కోసం పంపాను.",
        "req_fail": "క్షమించండి {name}. మీకు {bal} {kind} సెలవులు మాత్రమే మిగిలి ఉన్నాయి, కాబట్టి {days} రోజులు పంపలేకపోయాను.",
        "holidays": "నమస్కారం {name}. రాబోయే సెలవులు: {list}.",
        "unknown": "క్షమించండి, నాకు అర్థం కాలేదు. సెలవుల బ్యాలెన్స్, పేస్లిప్ తేదీ, పండుగల జాబితా అడగవచ్చు లేదా సెలవుకు దరఖాస్తు చేయవచ్చు.",
    },
}

KIND_WORD = {
    "en": {"casual": "casual", "sick": "sick", "earned": "earned"},
    "hi": {"casual": "आकस्मिक", "sick": "बीमारी", "earned": "अर्जित"},
    "te": {"casual": "క్యాజువల్", "sick": "సిక్", "earned": "ఎర్న్డ్"},
}


def _resolve_start(start) -> date:
    if isinstance(start, str):
        if start == "tomorrow":
            return date.today() + timedelta(days=1)
        try:
            return date.fromisoformat(start)
        except ValueError:
            pass
    return date.today()


def handle(
    emp_id: str,
    text: str,
    detected_lang: str | None,
    default_voice: str = "Nalini",
    force_intent: dict | None = None,
    force_lang: str | None = None,
) -> dict:
    """Full turn: text -> intent -> HR action -> reply text (in the user's language).

    force_intent: skip understanding and use this intent dict directly (source = 'button').
    force_lang:   override language family ('en', 'hi', or 'te') regardless of detected_lang.
    """
    # Language: forced override > detected > default (en)
    lang = force_lang if force_lang in ("en", "hi", "te") else lang_family(detected_lang)

    # Intent: forced override > LLM/rules
    if force_intent is not None:
        intent, source = force_intent, "button"
    else:
        intent, source = understand(text)

    name = hr_data.EMPLOYEES[emp_id]["name"].split()[0]
    tpl = REPLIES[lang]
    action = None
    tts_voice = TTS_VOICE.get(lang) or default_voice

    kind = intent.get("leave_type") if intent.get("leave_type") in ("casual", "sick", "earned") else "casual"
    if intent["intent"] == "leave_balance":
        reply = tpl["balance"].format(name=name, **hr_data.leave_balance(emp_id))
    elif intent["intent"] == "payslip_date":
        p = hr_data.payslip_info(emp_id)
        reply = tpl["payslip"].format(name=name, date=p["date"].strftime("%d %B"), net=p["net_pay"])
    elif intent["intent"] == "leave_request":
        days = int(intent.get("days") or 1)
        start = _resolve_start(intent.get("start"))
        action = hr_data.create_leave_request(emp_id, days, start, kind)
        key = "req_ok" if action["ok"] else "req_fail"
        reply = tpl[key].format(name=name, days=days, kind=KIND_WORD[lang][kind],
                                start=start.strftime("%d %B"), bal=action["balance"])
    elif intent["intent"] == "holiday_list":
        holidays = hr_data.upcoming_holidays(3)
        name_key = "name_hi" if lang == "hi" else "name_te" if lang == "te" else "name_en"
        OPT = {"en": " (optional)", "hi": " (वैकल्पिक)", "te": " (ఐచ్ఛికం)"}
        def _fmt(h: dict) -> str:
            label = h[name_key]
            if h.get("restricted"):
                label += OPT[lang]
            return f"{h['date'].strftime('%d %b')} – {label}"
        items = ", ".join(_fmt(h) for h in holidays)
        reply = tpl["holidays"].format(name=name, list=items)
    else:
        reply = tpl["unknown"]

    return {"lang": lang, "tts_lang": TTS_LANG[lang], "tts_voice": tts_voice, "intent": intent,
            "intent_source": source, "reply": reply, "action": action}
