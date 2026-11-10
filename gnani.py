"""Thin clients for Gnani AI's Vachana APIs: Prisma (STT) and Timbre (TTS).

Endpoints and payloads follow https://docs.gnani.ai/api/introduction/quick-start
"""
import os
import time

import requests

BASE = "https://api.vachana.ai"


class GnaniError(RuntimeError):
    pass


def _headers() -> dict:
    key = os.environ.get("GNANI_API_KEY")
    if not key:
        raise GnaniError("GNANI_API_KEY is not set. Put it in your .env file.")
    return {"X-API-Key-ID": key}


def transcribe(audio_bytes: bytes, filename: str = "audio.wav",
               language_code: str = "indic-auto") -> tuple[str, str | None]:
    """Prisma v3.0 speech-to-text. Audio: wav/mp3/ogg/flac/aac/m4a, <=30 s.

    language_code: "indic-auto" (auto-detect) or e.g. "hi-IN", "te-IN", "en-IN".
    Returns (transcript, detected_language_code).
    """
    try:
        r = requests.post(
            f"{BASE}/stt/v3",
            headers=_headers(),
            files={"audio_file": (filename, audio_bytes, "audio/wav")},
            data={"model": "prisma-v3.0", "language_code": language_code},
            timeout=60,
        )
    except requests.exceptions.RequestException as e:
        raise GnaniError(f"STT network error: {e}") from e
    if not r.ok:
        raise GnaniError(f"STT failed ({r.status_code}): {r.text[:300]}")
    j = r.json()
    if not j.get("success", True):
        raise GnaniError(f"STT error: {j}")
    return j.get("transcript", "").strip(), j.get("detected_language_code")


def synthesize(text: str, language: str = "hi-IN", voice: str = "Nalini",
               speed: float = 1.0) -> bytes:
    """Timbre v2.5 text-to-speech. Returns WAV bytes. Retries on dropped connections."""
    payload = {
        "text": text, "voice": voice, "model": "timbre-v2.5",
        "language": language, "speed": speed,
        "audio_config": {"sample_rate": 24000, "num_channels": 1,
                         "sample_width": 2, "encoding": "linear_pcm",
                         "container": "wav"},
    }
    last_err = None
    for attempt in range(3):
        try:
            r = requests.post(
                f"{BASE}/api/v1/tts/inference",
                headers={**_headers(), "Content-Type": "application/json"},
                json=payload, timeout=60,
            )
            if r.ok:
                return r.content
            last_err = f"{r.status_code}: {r.text[:200]}"
            if r.status_code < 500:      # 4xx will not fix itself
                break
        except requests.exceptions.RequestException as e:
            last_err = str(e)
        time.sleep(1.5 * (attempt + 1))
    raise GnaniError(f"TTS failed after retries: {last_err}")
