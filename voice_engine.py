from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class VoiceState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    THINKING = "thinking"
    SPEAKING = "speaking"
    EXECUTING = "executing"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    OFFLINE = "offline"


class LanguageMode(str, Enum):
    AUTO = "auto"
    ENGLISH = "english"
    YORUBA = "yoruba"


@dataclass
class TranscriptionResult:
    text: str
    language: str
    provider: str
    confidence: float | None = None


@dataclass
class SpeechResult:
    audio_available: bool
    provider: str
    text_fallback: str
    reason: str | None = None


class VoiceEngine:
    """
    Speech interface for David AI. No speech-to-text or text-to-speech
    provider is wired in yet -- this class defines the contract so a
    real provider (e.g. AssemblyAI for STT, ElevenLabs for TTS) can be
    dropped in later without changing any caller. Calling transcribe()
    or synthesize() today returns an honest "not configured" result
    rather than fabricating audio or text.

    Language handling: AUTO is the default. English and Yoruba are the
    two supported language modes; if Yoruba speech output isn't
    available from the configured provider, callers should surface the
    text_fallback and clearly say voice output isn't available, per the
    "never fake unsupported capabilities" requirement.
    """

    SUPPORTED_LANGUAGES = ("english", "yoruba")

    def __init__(self, stt_provider: str | None = None, tts_provider: str | None = None) -> None:
        self.stt_provider = stt_provider
        self.tts_provider = tts_provider

    def detect_language(self, text: str) -> str:
        """Very small heuristic placeholder; a real implementation would use
        a language-ID model. Defaults to English when uncertain."""
        yoruba_markers = ("ọ", "ẹ", "ṣ", "bawo", "pele", "e se")
        lowered = text.lower()
        if any(marker in lowered for marker in yoruba_markers):
            return "yoruba"
        return "english"

    async def transcribe(self, audio_bytes: bytes, language_mode: LanguageMode = LanguageMode.AUTO) -> TranscriptionResult:
        if not self.stt_provider:
            return TranscriptionResult(
                text="",
                language=language_mode.value,
                provider="none",
                confidence=None,
            )
        # Real STT call would happen here once a provider is configured.
        return TranscriptionResult(text="", language=language_mode.value, provider=self.stt_provider)

    async def synthesize(self, text: str, language_mode: LanguageMode = LanguageMode.AUTO) -> SpeechResult:
        language = language_mode.value if language_mode != LanguageMode.AUTO else self.detect_language(text)

        if not self.tts_provider:
            return SpeechResult(
                audio_available=False,
                provider="none",
                text_fallback=text,
                reason="No text-to-speech provider is configured yet.",
            )

        if language == "yoruba":
            # Placeholder: many TTS providers don't support Yoruba output.
            # Until a provider that does is confirmed and wired in, be
            # explicit rather than pretending audio was generated.
            return SpeechResult(
                audio_available=False,
                provider=self.tts_provider,
                text_fallback=text,
                reason="Yoruba voice output isn't available from the configured provider yet; continuing in Yoruba text.",
            )

        return SpeechResult(audio_available=False, provider=self.tts_provider, text_fallback=text,
                             reason="Voice synthesis integration not yet implemented for this provider.")
