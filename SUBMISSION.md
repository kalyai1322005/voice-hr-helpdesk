# Submission drafts (fill in the [brackets] before posting)

---

## LinkedIn / X post

I built a **Voice HR Helpdesk** for India's workforce using @GnaniAI 🎙️

Ask HR in Hindi, Telugu or Hinglish, out loud:
> *"నా జీతం ఎప్పుడు వస్తుంది?"* / *"मेरी कितनी छुट्टियां बाकी हैं?"*

…and hear the answer back in the **same language**. Apply for leave, check payslip dates, and even ask for the company holiday list — all by voice.

**How it works:**
🔹 **Gnani Prisma v3.0** — speech-to-text for Indian languages (auto-detect)
🔹 Rule-based intent detection (4 intents), LLM-ready via LLM_BASE_URL
🔹 HR system lookup — modelled on Oracle Fusion HCM APIs
🔹 **Gnani Timbre v2.5** — spoken reply in your language

**Why it matters:** Most HR self-service is English-only text. A voice helpdesk in regional languages makes HR accessible to frontline and non-desk employees across India.

Built in **[hours spent]** hours as part of the Great Indian AI Internship Challenge.
Code: [GitHub link]

#GnaniAI #GreatIndianAIInternshipChallenge #IndianLanguages #VoiceAI

> _(Tag the official Gnani AI LinkedIn/X account. Attach the 60-second demo video.)_

---

## Written project explanation

**Problem.**
Employee HR queries — leave balance, payslip date, leave requests, holiday calendar — are handled through English-only portals and ticketing systems. Many employees prefer to speak in Hindi, Telugu or Hinglish, and HR teams spend significant time answering the same repetitive questions.

**Solution.**
A voice-first HR helpdesk. The employee speaks; Gnani Prisma v3.0 transcribes with automatic Indic language detection; a keyword-based intent classifier (4 rules, one per supported action) picks the right HR function; the app reads or writes HR data; Gnani Timbre v2.5 speaks the answer in the detected language. An LLM can replace the keyword classifier with no code change — just set `LLM_BASE_URL` and `LLM_MODEL` in `.env`.

**Supported intents (4):**
1. **Leave balance** — reports casual, sick and earned days remaining
2. **Payslip date** — returns payslip availability date and net pay
3. **Leave request** — validates against available balance and submits for manager approval
4. **Holiday list** — returns the next upcoming gazetted / restricted holidays (2026–2027 Central Govt list)

**Gnani models / APIs used:**
- **Gnani Prisma v3.0** — STT via `POST https://api.vachana.ai/stt/v3`, header `X-API-Key-ID`, field `language_code=indic-auto` for automatic Indic language detection
- **Gnani Timbre v2.5** — TTS via `POST https://api.vachana.ai/api/v1/tts/inference`, returns WAV audio played back in the browser
- Intent detection is **rule-based** (keyword matching across English / Hindi / Telugu / Hinglish); the code is **LLM-ready** — set `LLM_BASE_URL` / `LLM_MODEL` in `.env` to route through any OpenAI-compatible endpoint (e.g. Gnani Evon v3.3 on vLLM)

**Users.**
Enterprise HR teams and employees — especially non-desk, frontline and regional-language workers across India.

**Design choices.**
- Replies use fixed templates filled from HR data, so numbers and dates spoken back are never hallucinated by a model.
- Leave requests are validated against the employee's balance before submission.
- The intent layer degrades gracefully: LLM (if configured) → keyword rules → "unknown" fallback with helpful guidance in the user's language.
- STT and TTS failures show a friendly warning; the text reply is always shown even if audio fails.

**Real-world path.**
The mock data layer maps one-to-one to Oracle Fusion HCM REST resources (absences, payslips, publicHolidays), so it can be connected to a real HCM tenant with minimal changes. Add SSO/OAuth 2.0 for employee identity.

**Contributions.**
[my name]: design, development, testing, demo video.

---

## 60-second demo script

| Time | Action |
|---|---|
| 0–10 s | "HR portals are English-only. I built a voice helpdesk in Indian languages." — show the app UI |
| 10–22 s | Click **🏖️ Leave Balance** → metrics appear + spoken reply |
| 22–34 s | Type *"मेरी कितनी छुट्टियां बाकी हैं?"* → Hindi reply plays |
| 34–44 s | Click **🎉 Holidays** → holiday list with optional/gazetted tags |
| 44–54 s | Click **📝 Apply Leave** → leave row appears in the table |
| 54–60 s | Expand **"Behind the scenes"** → show Prisma → intent → HR action → Timbre |

---

## Hours spent

[hours spent]

## GitHub repository

[GitHub link]

## Social post link

[LinkedIn/X post link]
