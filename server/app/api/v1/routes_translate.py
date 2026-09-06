from fastapi import APIRouter

router = APIRouter(prefix='/translate', tags=['translation'])


@router.post('')
def translate(payload: dict):
    return payload


@router.post('/voice-input')
def voice_input():
    return {'transcript': ''}


@router.post('/voice-output')
def voice_output(payload: dict):
    return payload
