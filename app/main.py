from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importing from your specific router files
from app.routers import (
    auth,      # The new router we just built
    badges, 
    events, 
    quizzes, 
    sessions, 
    users, 
    roles,     # For fetching role strings
    location   # For fetching location strings
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

# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check() -> dict:
    """Simple health check endpoint."""
    return {"status": "ok"}