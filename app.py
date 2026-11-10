"""Voice HR Helpdesk - speak in Hindi / Telugu / Hinglish / English, get a spoken answer.

Pipeline: mic -> Gnani Prisma (STT) -> intent (LLM or rules) -> HR data -> Gnani Timbre (TTS)
Run:  streamlit run app.py
"""
import hashlib
import os

import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import brain
import gnani
import hr_data

st.set_page_config(page_title="Voice HR Helpdesk", page_icon="🎙️", layout="wide")

# ── Header ──────────────────────────────────────────────────────────────────
st.title("🎙️ Voice HR Helpdesk")
st.caption("Ask HR in your own language · Powered by Gnani AI")

# ── Pipeline banner ──────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:10px;padding:12px 20px;
            background:#0e1117;border:1px solid #262730;border-radius:10px;
            margin-bottom:4px;flex-wrap:wrap;font-size:0.95em;">
  <span>🎙️ <b style='color:#ff4b4b'>Mic</b></span>
  <span style='color:#555'>──▶</span>
  <span>🧠 <b style='color:#1dc8cd'>Prisma v3.0</b> <span style='color:#666;font-size:0.85em'>(STT)</span></span>
  <span style='color:#555'>──▶</span>
  <span>🔍 <b style='color:#f5a623'>Intent</b></span>
  <span style='color:#555'>──▶</span>
  <span>🗄️ <b style='color:#7ed321'>HR Data</b></span>
  <span style='color:#555'>──▶</span>
  <span>🔊 <b style='color:#a855f7'>Timbre v2.5</b> <span style='color:#666;font-size:0.85em'>(TTS)</span></span>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("👤 Employee")
    emp_id = st.selectbox("Signed in as", list(hr_data.EMPLOYEES),
                          format_func=lambda i: f"{hr_data.EMPLOYEES[i]['name']} ({i})")
    st.header("⚙️ Settings")

    # key= pins both widgets to session_state so button clicks never reset them.
    if "stt_lang" not in st.session_state:
        st.session_state["stt_lang"] = "indic-auto"
    stt_lang = st.selectbox(
        "Speech language",
        ["indic-auto", "hi-IN", "te-IN", "en-IN"],
        index=0,
        key="stt_lang",
        help="indic-auto lets Prisma v3.0 detect the language.",
    )

    if "reply_lang" not in st.session_state:
        st.session_state["reply_lang"] = "Auto"
    reply_lang_label = st.radio(
        "Reply language",
        ["Auto", "English", "हिन्दी", "తెలుగు"],
        key="reply_lang",
        help="Auto = follow the detected / typed language. Force a language for Quick Demo buttons, mic, and typed input.",
    )

    voice = st.text_input("Timbre voice", os.environ.get("GNANI_VOICE", "Nalini"),
                          help="Pick a name from the Gnani Voice Catalog.")
    has_key = bool(os.environ.get("GNANI_API_KEY"))
    st.write("Gnani API key:", "✅ found" if has_key else "❌ missing (typed mode only)")
    st.write("LLM intent:", "✅ " + os.environ["LLM_MODEL"] if os.environ.get("LLM_MODEL") else "⚙️ rules fallback")

    if st.button("Reset demo", use_container_width=True):
        st.session_state["last"] = None
        st.session_state["log"] = []
        st.session_state["last_audio"] = None
        st.rerun()

    st.header("🗓️ Upcoming Holidays 2026-27")
    for h in hr_data.upcoming_holidays(3):
        tag = " · *optional*" if h.get("restricted") else ""
        st.caption(f"**{h['date'].strftime('%d %b')}** – {h['name_en']}{tag}")

st.session_state.setdefault("log", [])
st.session_state.setdefault("last_audio", None)

# Map the radio label to a brain lang-family code (None = Auto).
_REPLY_LANG_MAP = {"Auto": None, "English": "en", "हिन्दी": "hi", "తెలుగు": "te"}
_forced_lang: str | None = _REPLY_LANG_MAP[reply_lang_label]


def run_turn(
    text: str,
    detected_lang: str | None,
    from_voice: bool,
    force_intent: dict | None = None,
):
    """Execute one full turn.

    force_intent: passed straight to brain.handle() for Quick Demo buttons.
    _forced_lang (closure): overrides the reply language when the user has
    picked English / Hindi / Telugu in the sidebar radio.
    """
    result = brain.handle(
        emp_id, text, detected_lang,
        default_voice=voice,
        force_intent=force_intent,
        force_lang=_forced_lang,
    )
    audio_out = None
    if has_key:
        try:
            tts_v = result.get("tts_voice") or voice
            audio_out = gnani.synthesize(result["reply"], language=result["tts_lang"], voice=tts_v)
        except Exception as e:
            st.warning(f"⚠️ TTS unavailable — text reply shown instead. ({e})")
    st.session_state["last"] = {"heard": text, "lang": detected_lang, "result": result,
                                "audio": audio_out, "voice": from_voice}
    if result["action"]:
        st.session_state["log"].append({"employee": emp_id, **{k: v for k, v in result["action"].items()
                                                               if k in ("type", "days", "start", "end", "status")}})


# ── Quick Demo buttons ────────────────────────────────────────────────────────
# Each entry: (button label, {lang: "Heard:" phrase}, force_intent dict)
# The intent is passed directly — no keyword matching needed.
DEMO_QUERIES = [
    (
        "🏖️ Leave Balance",
        {
            "en": "How many leaves do I have left?",
            "hi": "मेरी कितनी छुट्टियां बाकी हैं?",
            "te": "నా సెలవులు ఎన్ని మిగిలి ఉన్నాయి?",
        },
        {"intent": "leave_balance"},
    ),
    (
        "💰 Payslip Date",
        {
            "en": "When is my salary?",
            "hi": "मेरी सैलरी कब आएगी?",
            "te": "నా జీతం ఎప్పుడు వస్తుంది?",
        },
        {"intent": "payslip_date"},
    ),
    (
        "📝 Apply Leave",
        {
            "en": "I need 2 days casual leave from tomorrow",
            "hi": "मुझे कल से 2 दिन की छुट्टी चाहिए",
            "te": "రేపు నుండి 2 రోజులు సెలవు కావాలి",
        },
        {"intent": "leave_request", "days": 2, "start": "tomorrow", "leave_type": "casual"},
    ),
    (
        "🎉 Holidays",
        {
            "en": "Show upcoming holidays",
            "hi": "आने वाले त्योहार दिखाओ",
            "te": "రాబోయే సెలవులు చూపించు",
        },
        {"intent": "holiday_list"},
    ),
]

st.subheader("⚡ Quick Demo")
q_cols = st.columns(4)
for col, (label, phrases, intent_dict) in zip(q_cols, DEMO_QUERIES):
    if col.button(label, use_container_width=True):
        # Pick the display phrase matching the forced language (Auto → English).
        phrase_lang = _forced_lang or "en"
        heard_text = phrases[phrase_lang]
        # detected_lang for TTS routing mirrors the chosen lang code.
        detected_lang_code = {"en": "en-IN", "hi": "hi-IN", "te": "te-IN"}[phrase_lang]
        with st.spinner("Thinking..."):
            run_turn(heard_text, detected_lang_code, False, force_intent=intent_dict)

st.divider()

# ── Main columns ──────────────────────────────────────────────────────────────
left, right = st.columns([1, 1])

with left:
    st.subheader("1. Speak")
    audio = st.audio_input("Tap to record (max 30 seconds)")
    if audio is not None:
        data = audio.getvalue()
        digest = hashlib.md5(data).hexdigest()
        if digest != st.session_state["last_audio"]:
            st.session_state["last_audio"] = digest
            if not has_key:
                st.error("Add GNANI_API_KEY to .env to use voice. You can still type below.")
            else:
                with st.spinner("🧠 Prisma is listening..."):
                    try:
                        text, lang = gnani.transcribe(data, language_code=stt_lang)
                    except Exception as e:
                        st.warning(f"⚠️ Speech recognition failed: {e}")
                        text, lang = "", None
                if text:
                    with st.spinner("Thinking..."):
                        run_turn(text, lang, True)
                else:
                    st.warning("I could not hear that, please try again.")

    st.subheader("or type")
    with st.form("type_form", clear_on_submit=True, border=False):
        typed = st.text_input("Type a question (any language)", placeholder="मेरी कितनी छुट्टियां बाकी हैं?")
        asked = st.form_submit_button("Ask")
    if asked and typed.strip():
        # Script-detect when Auto; honour forced lang for TTS routing.
        guess = "te-IN" if any("ఀ" <= ch <= "౿" for ch in typed) else \
                "hi-IN" if any("ऀ" <= ch <= "ॿ" for ch in typed) else "en-IN"
        with st.spinner("Thinking..."):
            run_turn(typed.strip(), guess, False)

with right:
    st.subheader("2. Answer")
    last = st.session_state.get("last")
    if last:
        intent_name = last["result"]["intent"].get("intent", "unknown")
        INTENT_EMOJI = {
            "leave_balance": "🏖️",
            "payslip_date":  "💰",
            "leave_request": "📝",
            "holiday_list":  "🎉",
            "unknown":       "❓",
        }
        emoji = INTENT_EMOJI.get(intent_name, "💬")

        badge = "🎙️ Voice → Gnani Prisma v3.0" if last.get("voice") else "⌨️ Typed"
        if hasattr(st, "badge"):
            st.badge(badge, color="blue" if last.get("voice") else "gray")
        else:
            st.caption(f":grey-background[{badge}]")

        st.markdown(f"**Heard:** {last['heard']}")
        st.caption(
            f"Language: `{last['lang']}` · Intent: {emoji} `{intent_name}` "
            f"via *{last['result']['intent_source']}*"
        )

        # Leave balance → show pretty metrics
        if intent_name == "leave_balance":
            bal = hr_data.leave_balance(emp_id)
            m1, m2, m3 = st.columns(3)
            m1.metric("🏖️ Casual",  bal["casual"],  "days")
            m2.metric("🤒 Sick",    bal["sick"],    "days")
            m3.metric("💼 Earned",  bal["earned"],  "days")

        st.success(last["result"]["reply"])
        if last["audio"]:
            st.audio(last["audio"], format="audio/wav", autoplay=True)

        with st.expander("🔬 Behind the scenes (for the demo video)"):
            st.json({"stt": "Gnani Prisma v3.0", "intent": last["result"]["intent"],
                     "hr_action": last["result"]["action"], "tts": "Gnani Timbre v2.5"})
    else:
        st.info("👆 Click a Quick Demo button, record audio, or type a question to begin.")

# ── Leave log ─────────────────────────────────────────────────────────────────
st.subheader("📋 Leave Requests Submitted This Session")
if st.session_state["log"]:
    st.dataframe(st.session_state["log"], use_container_width=True)
else:
    st.caption("None yet. Try: 'I need 2 days casual leave from tomorrow'.")
