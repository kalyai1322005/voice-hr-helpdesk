# 🎬 Voice HR Helpdesk — 75-Second Demo Script

---

## ✅ Pre-Recording Checklist

Before you press Record, verify every item below:

- [ ] **Speech language = `indic-auto`** in the sidebar (not `te-IN` or `hi-IN`)
- [ ] **Click "Reset demo"** in the sidebar — clears the last answer and leave table
- [ ] **Microphone allowed** in the browser (address bar → lock icon → Microphone → Allow)
- [ ] **Volume up** — the spoken reply must be audible in the recording
- [ ] **Close all other browser tabs** — no distractions visible
- [ ] **No `.env` or API key visible** on screen — keep the sidebar scroll position above Settings if needed
- [ ] Screen resolution / zoom set so the full UI is visible without scrolling

---

## 🎙️ Script

### 0:00 – 0:10 · Problem statement *(speak to camera, app UI visible in background)*

> "Most HR portals are English-only text — leaving millions of frontline and
> regional-language workers unable to self-serve in their own language.
> I built a voice HR helpdesk using Gnani AI, so employees can ask in
> Hindi, Telugu, or Hinglish — and hear the answer spoken back."

---

### 0:10 – 0:25 · Hindi by MIC — leave balance *(click mic, speak, wait for audio reply)*

**Action:** Click the microphone button under "1. Speak".

**Say clearly into the mic:**
> *"मेरी कितनी छुट्टियां बाकी हैं?"*
> *(Meri kitni chhutiyan baaki hain?)*

**While the reply plays, narrate:**
> "Gnani Prisma v3.0 detected Hindi automatically — no language switch needed.
> The leave balance metrics appear, and Timbre v2.5 speaks the answer in Hindi."

---

### 0:25 – 0:40 · Telugu by MIC — payslip date *(click mic, speak, wait for audio reply)*

**Action:** Click the microphone button again.

**Say clearly into the mic:**
> *"నా జీతం ఎప్పుడు వస్తుంది?"*
> *(Naa jeetam eppudu vasthundi?)*

**While the reply plays, narrate:**
> "Now Telugu. Same pipeline — Prisma detects the language, the HR data
> layer returns the payslip date, and Timbre speaks back in Telugu."

---

### 0:40 – 0:55 · Hinglish by MIC — apply leave *(click mic, speak, then point at the leave table)*

**Action:** Click the microphone button.

**Say clearly into the mic:**
> *"Kal ke liye 2 din ki leave apply karni hai"*

**After the reply plays, pan to the leave request table at the bottom:**
> "The request is validated against the employee's available balance and
> logged here — ready to be sent to a manager approval workflow."

---

### 0:55 – 1:10 · Behind the scenes *(click to expand the expander)*

**Action:** Click **"🔬 Behind the scenes (for the demo video)"** expander in the Answer panel.

**Narrate while pointing to the JSON:**
> "Here's the full pipeline in one place:
> **Gnani Prisma v3.0** handles speech-to-text with `indic-auto` language detection.
> The intent step — rule-based, with an LLM drop-in slot — picks the right HR action.
> **Gnani Timbre v2.5** turns the reply text into natural-sounding speech in the
> detected language. No English hardcoding anywhere."

---

### 1:10 – 1:15 · Close *(look at camera)*

> "Built with Gnani AI for the Great Indian AI Internship Challenge.
> All source code is on GitHub — link in the description."

---

## 📝 Notes

- Each MIC segment: allow ~3 s for Prisma to transcribe, then another ~3 s for Timbre to synthesise. The total 15 s per segment accounts for this.
- If a mic recording is too quiet, re-record that segment and splice it in.
- Keep the sidebar visible throughout so viewers can see `indic-auto` is set.
- The "Behind the scenes" JSON should be legible — zoom in if needed before expanding.

