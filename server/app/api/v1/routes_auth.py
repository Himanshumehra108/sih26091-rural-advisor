# server/app/api/v1/routes_auth.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == payload.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    new_user = User(
        name=payload.name,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        preferred_language=payload.preferred_language,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id)})
    return {"success": True, "data": {"user_id": str(new_user.id), "token": token}, "error": None}


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == payload.phone).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid phone or password")

    token = create_access_token({"sub": str(user.id)})
    return {"success": True, "data": {"user_id": str(user.id), "token": token}, "error": None}