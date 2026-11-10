# Voice HR Helpdesk (Telugu / Hindi / Hinglish / English)

**Problem:** Most enterprise HR portals are English-only text interfaces — leaving frontline and regional-language workers unable to self-serve in their own language.

This voice-first helpdesk lets employees ask HR questions by speaking in Telugu, Hindi, Hinglish or English and hear the answer spoken back in the same language.

---

## Pipeline

```
🎙️ Voice ──▶ Gnani Prisma v3.0 (STT) ──▶ Intent detection ──▶ HR data ──▶ Gnani Timbre v2.5 (TTS) ──▶ 🔊 Spoken reply
```

---

## Models Used

| Model / Component | Purpose & Implementation |
|---|---|
| **Gnani Prisma v3.0** | Speech-to-text (STT) — `POST https://api.vachana.ai/stt/v3` with `language_code=indic-auto` for automatic Indic language detection |
| **Gnani Timbre v2.5** | Text-to-speech (TTS) — `POST https://api.vachana.ai/api/v1/tts/inference`, returns WAV audio |
| **Intent Detection** | Rule-based keyword matching (English / Hindi / Telugu / Hinglish); **LLM-ready** via `LLM_BASE_URL` in `.env` — configure `LLM_BASE_URL`, `LLM_MODEL`, and `LLM_API_KEY` to route requests through any OpenAI-compatible LLM endpoint (e.g., Gnani Evon v3.3 on vLLM) |

---

## Setup Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure secrets
copy .env.example .env        # Windows
# cp .env.example .env        # Mac / Linux
# → Open .env and paste your GNANI_API_KEY from https://app.gnani.ai

# 3. Run the application
streamlit run app.py
```

> **Note:** No API key? Typed mode works without an API key — text replies are generated and displayed, while audio synthesis requires `GNANI_API_KEY`.

---

## Supported Requests (4)

The helpdesk supports 4 common HR requests across English, Hindi, Telugu, and Hinglish:

| Request | Sample Queries | Action & Response |
|---|---|---|
| **1. Leave Balance** | *"How many leaves do I have left?"* / *"मेरी कितनी छुट्टियां बाकी हैं?"* / *"నాకు ఎన్ని సెలవులు ఉన్నాయి?"* | Returns remaining casual, sick, and earned leave days |
| **2. Payslip Date** | *"When is my salary?"* / *"मेरी सैलरी कब आएगी?"* / *"నా జీతం ఎప్పుడు వస్తుంది?"* | Returns payslip availability date and net pay |
| **3. Leave Request** | *"I need 2 days casual leave from tomorrow"* / *"कल से 2 दिन की छुट्टी चाहिए"* / *"రేపటి నుండి 2 రోజుల క్యాజువల్ సెలవు కావాలి"* | Validates requested days against available balance and submits request for manager approval |
| **4. Holidays (2026–27)** | *"Show upcoming holidays"* / *"त्योहार कब हैं?"* / *"రాబోయే సెలవులు ఏమిటి?"* | Returns the next upcoming public and restricted holidays from the 2026–2027 calendar |

Replies are spoken back **in the language used by the employee**.

---

## HR Data & Oracle Fusion HCM Mapping

All employee records in `hr_data.py` are mock data for demonstration purposes. Each operation directly maps to standard Oracle Fusion HCM REST resources:

| Function | Oracle Fusion HCM REST Resource | Description |
|---|---|---|
| `leave_balance()` | `GET /absences` | Fetches employee accrual balances (casual, sick, earned) |
| `payslip_info()` | `GET /payslips` | Retrieves latest payslip payment date and net salary |
| `create_leave_request()` | `POST /absences` | Submits a leave transaction and initiates manager approval workflow |
| `upcoming_holidays()` | `GET /publicHolidays` | Queries public, national, and gazetted holiday calendars |

Holiday dates follow the Central Government holiday list for 2026–2027 (including gazetted and optional/restricted holidays).

---

## Project Structure

| File | Role |
|---|---|
| `app.py` | Streamlit UI — voice recorder, typing fallback, quick demo buttons, answer badge & card, session leave log |
| `brain.py` | Intent detection (rule-based keyword classifier + optional LLM fallback) + multilingual reply generation + TTS voice mapping |
| `gnani.py` | REST clients for Gnani Prisma v3.0 (STT) and Gnani Timbre v2.5 (TTS) |
| `hr_data.py` | Mock HR data records and Central Govt 2026–2027 holiday lists |
| `.env.example` | Environment variable template |

---

Built for the **Gnani AI Great Indian AI Internship Challenge**.
