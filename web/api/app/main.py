"""
main.py
=======
FastAPI application entry point for StartRightDay backend.

Routes:
  POST /api/v1/recommend  →  generate_recommendation()

CORS is configured for Flutter dev (localhost:* and any origin during development).
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.models import RecommendationRequest, RecommendationResponse
from app.predictor import generate_recommendation

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("startrightday")


# ---------------------------------------------------------------------------
# Application lifespan (startup/shutdown hooks)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("StartRightDay backend starting up...")
    yield
    logger.info("StartRightDay backend shutting down.")


# ---------------------------------------------------------------------------
# FastAPI instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="StartRightDay API",
    description=(
        "Vedic Panchang-based auspicious timing recommendations. "
        "Deterministic, rule-based, fully explainable."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — allow Flutter dev clients
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict in production to your app's domain
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# ---------------------------------------------------------------------------
# Global exception handler for clean error responses
# ---------------------------------------------------------------------------
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    logger.warning("ValueError: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred. Please try again."},
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health_check() -> dict:
    """Liveness probe."""
    return {"status": "ok", "service": "StartRightDay"}


@app.post(
    "/api/v1/recommend",
    response_model=RecommendationResponse,
    tags=["Recommendation"],
    summary="Get auspicious time intervals for a given activity date",
    response_description="Auspicious time intervals with Panchang details and recommended activities",
)
async def recommend(request: RecommendationRequest) -> RecommendationResponse:
    """
    **Main endpoint.**

    Given birth details and an activity date, returns:
    - `status`: "auspicious" or "avoid"
    - `intervals`: List of auspicious time windows (empty if avoid)
    - `intervals[].panchang`: Nakshatra, Tithi, Yoga, Karana, Tara
    - `intervals[].activities`: Recommended activity categories

    No ML, no predictions. Pure Vedic Panchang rule engine.
    """
    logger.info(
        "Recommendation request: place=%s, birth=%s %s, activity=%s",
        request.birth_place,
        request.birth_date,
        request.birth_time,
        request.activity_date,
    )
    result = await generate_recommendation(request)
    logger.info("Result: status=%s, intervals=%d", result.status, len(result.intervals))
    return result
