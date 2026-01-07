from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from threading import Thread
from app.background.badge_worker import run_badge_worker
from app.background.tier_badge_worker import run_tier_badge_worker

# Importing from your specific router files
from app.routers import (
    auth,      # The new router we just built
    badges, 
    events, 
    quizzes,
    questions, 
    sessions, 
    users, 
    roles,     # For fetching role strings
    location,
    bonus,
    profile   # For fetching location strings
)
from app.config import get_settings

app = FastAPI(title="Stomata Labs Gamification API", version="1.0.0", redirect_slashes=False)

settings = get_settings()

# ---------------------------------------------------------
# CORS (allow Streamlit frontend)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

# Auth is the primary entry point
app.include_router(auth.router)

# Public Lookups (Used by the signup form dropdowns)
app.include_router(roles.router)
app.include_router(location.router)

# Protected Business Logic
app.include_router(users.router)
app.include_router(events.router)
app.include_router(sessions.router)
app.include_router(quizzes.router)
app.include_router(badges.router)
app.include_router(questions.router)
app.include_router(bonus.router)
app.include_router(profile.router)
# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check() -> dict:
    """Simple health check endpoint."""
    return {"status": "ok"}

@app.on_event("startup")
def start_background_workers():
    Thread(target=run_badge_worker, daemon=True).start()
    Thread(target=run_tier_badge_worker, daemon=True).start()