import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.bhashini_client import translate_with_sarvam

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/translate", tags=["translation"])


class TranslationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    source_language: str = "en-IN"
    target_language: str


SUPPORTED_TRANSLATION_CODES = {
    "en", "en-IN", "hi", "hi-IN", "pa", "pa-IN", "ta", "ta-IN", "te", "te-IN",
    "mr", "mr-IN", "bn", "bn-IN", "gu", "gu-IN", "kn", "kn-IN", "ml", "ml-IN",
    "or", "od-IN",
}


@router.post("")
def translate(payload: TranslationRequest):
    if payload.target_language not in SUPPORTED_TRANSLATION_CODES:
        return {"success": False, "data": {"translated_text": payload.text}, "error": "Unsupported target language"}

    try:
        translated = translate_with_sarvam(
            payload.text, payload.source_language, payload.target_language
        )
        return {"success": True, "data": {"translated_text": translated}, "error": None}
    except Exception:
        logger.exception("Dynamic translation failed for target language %s", payload.target_language)
        return {"success": True, "data": {"translated_text": payload.text}, "error": "Translation unavailable; original text returned"}


@router.post('/voice-input')
def voice_input():
    return {'transcript': ''}


@router.post('/voice-output')
def voice_output(payload: dict):
    return payload
