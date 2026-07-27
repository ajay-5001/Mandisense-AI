"""
MandiSense — FastAPI Application Entry Point
=============================================
Main FastAPI application with all API routes.

Run with:
    cd mandisense/backend
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import create_all_tables
from app.api.routes import router as api_router

# ─── App Setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="MandiSense API",
    description="Hyperlocal price intelligence for perishable goods vendors",
    version="0.1.0",
)

import os

# Get origins from environment, fallback to localhost and user's Vercel domains
origins_env = os.getenv("CORS_ORIGINS")
if origins_env:
    allowed_origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
else:
    allowed_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://mandisense-7v7zd1p9z-ajay902520-5616s-projects.vercel.app",
        "https://mandisense-ajay902520-5616s-projects.vercel.app",
        "https://mandisense-git-main-ajay902520-5616s-projects.vercel.app",
        "https://mandisense.vercel.app",
    ]

# CORS for frontend (Phase 3)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Include API Routes ───────────────────────────────────────────────────────
app.include_router(api_router)


@app.on_event("startup")
def startup():
    """Ensure database tables exist on startup."""
    create_all_tables()


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "app": "MandiSense",
        "version": "0.2.0",
        "status": "running",
        "phase": "Phase 2 — Recommendation Engine",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    """Health check for monitoring."""
    return {"status": "ok"}
