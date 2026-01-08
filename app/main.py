# app/main.py
from __future__ import annotations

import asyncio
import logging
from threading import Thread
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.background.badge_worker import run_badge_worker
from app.background.tier_badge_worker import run_tier_badge_worker
from app.services.stream_workers import start_stream_workers

# Routers: ensure these modules exist under app/routers and expose `router`
from app.routers import (
    auth,
    badges,
    events,
    quizzes,
    questions,
    sessions,
    users,
    roles,
    location,         # <-- ensure file is app/routers/location.py and exports `router`
    bonus,
    profile,
    anomaly_stream,
    optimizer_stream,
)

from app.config import get_settings
background_tasks = set()

# Silence noisy httpx / supabase logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("supabase").setLevel(logging.WARNING)
logging.getLogger("postgrest").setLevel(logging.WARNING)
logging.getLogger("gotrue").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

settings = get_settings()

app = FastAPI(
    title="Stomata Labs Gamification API",
    version="1.0.0",
    redirect_slashes=False,
)

# ---------------------------------------------------------
# CORS (allow Streamlit frontend)
# ---------------------------------------------------------
# Allow both localhost hostnames used by Streamlit; change to ["*"] for dev if needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://stomatalabs.streamlit.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------
# Public / auth
app.include_router(auth.router)

# Public lookups used by signup form dropdowns
app.include_router(roles.router)
app.include_router(location.router)

# Protected business logic
app.include_router(users.router)
app.include_router(events.router)
app.include_router(sessions.router)
app.include_router(quizzes.router)
app.include_router(badges.router)
app.include_router(questions.router)
app.include_router(bonus.router)
app.include_router(profile.router)
app.include_router(anomaly_stream.router)
app.include_router(optimizer_stream.router)

# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check() -> dict:
    """Simple health check endpoint."""
    return {"status": "ok"}


# ---------------------------------------------------------
# Startup: background workers / stream providers
# ---------------------------------------------------------
def _start_blocking_workers_in_threads() -> None:
    """
    Run legacy/blocking background workers in daemon threads so they don't block uvicorn.
    """
    try:
        Thread(target=run_badge_worker, daemon=True, name="badge-worker").start()
        Thread(target=run_tier_badge_worker, daemon=True, name="tier-badge-worker").start()
        logger.info("Started badge and tier badge workers in daemon threads.")
    except Exception as exc:
        logger.exception("Failed to start badge workers: %s", exc)


@app.on_event("startup")
async def startup_event():
    from threading import Thread
    from app.background.badge_worker import run_badge_worker
    from app.background.tier_badge_worker import run_tier_badge_worker

    Thread(target=run_badge_worker, daemon=True).start()
    Thread(target=run_tier_badge_worker, daemon=True).start()

    task = asyncio.create_task(start_stream_workers())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)