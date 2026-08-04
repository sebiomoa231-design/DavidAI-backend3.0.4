"""
Voice engine placeholder with stable API.
"""
from __future__ import annotations

from david.utils.logger import get_logger

logger = get_logger("david.voice")


class VoiceEngine:
    async def speech_to_text(self, audio_bytes: bytes, content_type: str = "audio/wav") -> dict:
        logger.info("speech_to_text called (placeholder)")
        return {
            "success": False,
            "text": "",
            "error": "Voice transcription is not implemented yet.",
            "content_type": content_type,
            "bytes_received": len(audio_bytes),
        }

    async def text_to_speech(self, text: str, voice: str = "default") -> dict:
        logger.info("text_to_speech called (placeholder)")
        return {
            "success": False,
            "audio_url": "",
            "error": "Text-to-speech is not implemented yet.",
            "voice": voice,
            "text": text,
        }


voice_engine = VoiceEngine()
