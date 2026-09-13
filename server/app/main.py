# server/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.models import user, report

from app.api.v1 import routes_calculator, routes_advisory, routes_auth, routes_reports

app = FastAPI(title="SIH Rural Advisor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(routes_calculator.router, prefix="/api/v1")
app.include_router(routes_advisory.router, prefix="/api/v1")
app.include_router(routes_auth.router, prefix="/api/v1")
app.include_router(routes_reports.router, prefix="/api/v1")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "SIH Rural Advisor API is running"}