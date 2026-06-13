#!/usr/bin/env python3
"""
NOIR VOICE INTERFACE v1.0 — SPEECH-TO-TEXT & TEXT-TO-SPEECH
============================================================
Tambahkan kemampuan suara ke AI agent Noir Sovereign.
AI dapat mendengar perintah suara dan merespons dengan suara.

Fitur:
  - Speech-to-Text: Rekam dari mikrofon → teks (via SpeechRecognition)
  - Text-to-Speech: Teks → suara (via pyttsx3 offline atau gTTS online)
  - Wake Word Detection: Dengarkan "Noir" → aktifkan mendengar
  - Continuous Listen Mode: Terus mendengarkan perintah
"""
import os
import time
import logging
import threading
import queue
import json
from datetime import datetime

log = logging.getLogger("NoirVoiceInterface")

# ── Deteksi dependensi ─────────────────────────────────────────────────────────
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False
    log.warning("[VOICE] speech_recognition tidak tersedia. pip install SpeechRecognition pyaudio")

try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    log.warning("[VOICE] pyttsx3 tidak tersedia. pip install pyttsx3")

NOIR_API_BASE = os.environ.get("NOIR_GATEWAY_URL", "http://localhost:80")
NOIR_API_KEY  = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")

_tts_engine = None
_tts_lock = threading.Lock()
_listen_active = False
_command_queue = queue.Queue()


# ── Text-to-Speech Engine ──────────────────────────────────────────────────────
def _init_tts():
    global _tts_engine
    if not HAS_TTS or _tts_engine is not None:
        return
    try:
        _tts_engine = pyttsx3.init()
        voices = _tts_engine.getProperty("voices")
        # Coba set suara Indonesia jika tersedia, fallback ke default
        id_voice = next((v for v in voices if "indonesia" in v.name.lower()), None)
        if id_voice:
            _tts_engine.setProperty("voice", id_voice.id)
        _tts_engine.setProperty("rate", 175)   # Kecepatan bicara
        _tts_engine.setProperty("volume", 0.9) # Volume 90%
        log.info("[VOICE] TTS engine diinisialisasi.")
    except Exception as e:
        log.error(f"[VOICE] Gagal inisialisasi TTS: {e}")
        _tts_engine = None

def speak(text: str, block: bool = True) -> dict:
    """
    Ubah teks menjadi suara dan putar melalui speaker.
    block=True → tunggu hingga selesai diucapkan.
    """
    if not HAS_TTS:
        log.warning(f"[VOICE] TTS tidak tersedia. Teks: {text[:80]}")
        return {"success": False, "message": "pyttsx3 tidak terinstal."}
    
    _init_tts()
    if _tts_engine is None:
        return {"success": False, "message": "TTS engine gagal diinisialisasi."}
    
    def _do_speak():
        with _tts_lock:
            try:
                _tts_engine.say(text)
                _tts_engine.runAndWait()
            except Exception as e:
                log.error(f"[VOICE] Error TTS: {e}")
    
    if block:
        _do_speak()
    else:
        threading.Thread(target=_do_speak, daemon=True).start()
    
    return {"success": True, "message": f"Diucapkan: {text[:60]}..."}


# ── Speech-to-Text Engine ──────────────────────────────────────────────────────
def listen_once(timeout: int = 5, phrase_limit: int = 10) -> dict:
    """
    Rekam audio dari mikrofon dan konversi ke teks (satu kali).
    Returns: {success, text, duration}
    """
    if not HAS_SR:
        return {"success": False, "text": "", "message": "SpeechRecognition tidak terinstal."}
    
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    
    try:
        with sr.Microphone() as source:
            log.info("[VOICE] Menyesuaikan noise ambient...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            log.info(f"[VOICE] Mendengarkan selama maks {timeout}s...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        
        # Coba Google Speech API dulu, fallback ke Sphinx (offline)
        try:
            text = recognizer.recognize_google(audio, language="id-ID,en-US")
            log.info(f"[VOICE] Teks terdengar: '{text}'")
            return {"success": True, "text": text, "engine": "google"}
        except sr.UnknownValueError:
            return {"success": False, "text": "", "message": "Suara tidak dapat dipahami."}
        except sr.RequestError:
            # Fallback ke offline Sphinx
            try:
                text = recognizer.recognize_sphinx(audio)
                return {"success": True, "text": text, "engine": "sphinx_offline"}
            except Exception:
                return {"success": False, "text": "", "message": "Tidak ada koneksi dan Sphinx tidak tersedia."}
    
    except sr.WaitTimeoutError:
        return {"success": False, "text": "", "message": "Tidak ada suara terdeteksi."}
    except Exception as e:
        return {"success": False, "text": "", "message": str(e)}


# ── Noir Chat via Voice ────────────────────────────────────────────────────────
def voice_chat_once() -> dict:
    """
    Satu siklus voice chat:
    1. Dengarkan perintah suara
    2. Kirim ke Brain AI via API
    3. Ucapkan balasan AI
    """
    speak("Siap mendengarkan.", block=False)
    
    result = listen_once(timeout=8, phrase_limit=15)
    if not result["success"]:
        speak("Maaf, saya tidak mendengar perintah Anda.")
        return result
    
    user_text = result["text"]
    log.info(f"[VOICE] Mengirim ke Brain: '{user_text}'")
    speak("Sedang diproses...", block=False)
    
    # Kirim ke Brain API
    import urllib.request
    try:
        data = json.dumps({"message": user_text, "context": "voice"}).encode()
        req = urllib.request.Request(
            NOIR_API_BASE + "/api/brain/chat",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {NOIR_API_KEY}"
            }
        )
        with urllib.request.urlopen(req, timeout=25) as r:
            resp = json.loads(r.read().decode())
        reply = resp.get("response") or resp.get("reply", "Tidak ada respons.")
    except Exception as e:
        reply = f"Gagal terhubung ke Brain: {e}"
    
    log.info(f"[VOICE] Brain menjawab: '{reply[:80]}'")
    speak(reply)
    
    return {"success": True, "user_text": user_text, "ai_reply": reply}


# ── Wake Word Continuous Mode ──────────────────────────────────────────────────
def start_wake_word_mode(wake_word: str = "noir", on_command=None):
    """
    Terus mendengarkan. Jika mendeteksi kata 'noir',
    aktifkan mode dengarkan perintah penuh.
    on_command: callback function(text) saat perintah dideteksi.
    """
    global _listen_active
    _listen_active = True
    
    log.info(f"[VOICE] Wake Word Mode aktif. Kata kunci: '{wake_word}'")
    speak(f"Mode Siaga Aktif. Ucapkan '{wake_word}' untuk memberi perintah.")
    
    if not HAS_SR:
        log.error("[VOICE] SpeechRecognition diperlukan untuk Wake Word Mode.")
        return
    
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 200
    recognizer.dynamic_energy_threshold = True
    
    while _listen_active:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
            
            try:
                text = recognizer.recognize_google(audio, language="id-ID,en-US").lower()
                if wake_word.lower() in text:
                    log.info(f"[VOICE] Wake word '{wake_word}' terdeteksi!")
                    result = voice_chat_once()
                    if on_command and result.get("user_text"):
                        on_command(result["user_text"], result.get("ai_reply", ""))
            except (sr.UnknownValueError, sr.RequestError):
                pass  # Diam, terus mendengarkan
        
        except sr.WaitTimeoutError:
            pass  # Normal, tidak ada suara
        except Exception as e:
            log.debug(f"[VOICE] Listen error: {e}")
            time.sleep(1)

def stop_wake_word_mode():
    global _listen_active
    _listen_active = False
    log.info("[VOICE] Wake Word Mode dihentikan.")


# ── CLI Demo ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    
    print("=== Noir Voice Interface Demo ===")
    print(f"TTS Available: {HAS_TTS}")
    print(f"STT Available: {HAS_SR}")
    
    if HAS_TTS:
        speak("Noir Sovereign Voice Interface aktif. Sistem berjalan dengan sempurna.")
    
    if HAS_SR:
        print("\nMode: Single Voice Chat")
        result = voice_chat_once()
        print(f"Result: {result}")
    else:
        print("\nInstall dependensi: pip install SpeechRecognition pyaudio pyttsx3")
