from fastapi import APIRouter
from pydantic import BaseModel

from app.services.voice_engine import LanguageMode, VoiceEngine

router = APIRouter(prefix="/voice", tags=["voice"])
engine = VoiceEngine()  # no STT/TTS provider configured yet


class SynthesizeRequest(BaseModel):
    text: str
    language_mode: LanguageMode = LanguageMode.AUTO


class SynthesizeResponse(BaseModel):
    audio_available: bool
    provider: str
    text_fallback: str
    reason: str | None = None


@router.get("/status")
def voice_status() -> dict:
    return {
        "stt_configured": engine.stt_provider is not None,
        "tts_configured": engine.tts_provider is not None,
        "supported_languages": list(engine.SUPPORTED_LANGUAGES),
        "default_language_mode": LanguageMode.AUTO.value,
    }


@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize(payload: SynthesizeRequest) -> SynthesizeResponse:
    result = await engine.synthesize(payload.text, payload.language_mode)
    return SynthesizeResponse(**result.__dict__)
