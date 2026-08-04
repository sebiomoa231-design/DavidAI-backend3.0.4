"""Voice engine placeholders with stable async interfaces."""
from __future__ import annotations

import base64

from david.utils.helpers import clip_text
from david.utils.logger import get_logger

logger = get_logger("david.voice")


async def speech_to_text(audio_bytes: bytes, content_type: str = "audio/wav") -> dict:
    logger.info(f"speech_to_text called ({content_type}, {len(audio_bytes)} bytes)")
    return {
        "success": False,
        "text": "",
        "language": "unknown",
        "error": "Voice-to-text is not configured yet. Add a speech provider to enable it.",
    }


async def text_to_speech(text: str, voice: str = "default") -> dict:
    logger.info(f"text_to_speech called (voice={voice}, text={clip_text(text, 50)})")
    # Return a safe, explicit placeholder payload so the UI can handle it gracefully.
    return {
        "success": False,
        "voice": voice,
        "audio_base64": "",
        "audio_content_type": "audio/mpeg",
        "error": "Text-to-speech is not configured yet. Add a voice provider to enable it.",
        "text": text,
    }
