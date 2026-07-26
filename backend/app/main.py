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

# CORS for frontend (Phase 3)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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
