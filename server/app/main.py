# server/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    routes_advisory,
    routes_calculator,
    routes_market,
    routes_reports,
    routes_translate,
)

app = FastAPI(title="SIH Rural Advisor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_calculator.router, prefix="/api/v1")
app.include_router(routes_advisory.router, prefix="/api/v1")
app.include_router(routes_market.router, prefix="/api/v1")
app.include_router(routes_reports.router, prefix="/api/v1")
app.include_router(routes_translate.router, prefix="/api/v1")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "SIH Rural Advisor API is running"}