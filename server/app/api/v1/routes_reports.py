from fastapi import APIRouter

router = APIRouter(prefix='/reports', tags=['reports'])


@router.get('')
def list_reports():
    return []


@router.post('')
def save_report(payload: dict):
    return payload
