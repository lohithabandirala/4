"""
AegisSphere — FastAPI Application
==================================
Asynchronous API orchestrator for real-time tournament operations.
Provides endpoints for crowd safety evaluation, transit routing,
supply chain monitoring, multilingual translation, and venue data.

Designed for serverless deployment (AWS Lambda via Mangum adapter)
with scale-to-zero capability and sub-millisecond cold starts.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import (
    CrowdMetrics,
    HealthResponse,
    OperationalResponse,
    SupplyChainResponse,
    TransitRequest,
    TransitResponse,
    TranslationRequest,
    TranslationResponse,
    VenueProfile,
)
from app.crowd_safety import evaluate_crowd_safety
from app.agent import evaluate_with_agent, evaluate_with_fallback
from app.guardrails import sanitize_input, check_domain_relevance
from app.transit_routing import generate_transit_route
from app.supply_chain import evaluate_supply_chain
from app.multilingual import translate_text, get_supported_languages
from app.venue_data import get_all_venue_profiles, get_venue_profile, VENUE_PROFILES


# ---------------------------------------------------------------------------
# Application Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup: Pre-load knowledge base
    from app.knowledge_loader import _load_stadium_policies
    _load_stadium_policies()
    yield
    # Shutdown: Cleanup resources


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AegisSphere Control Engine",
    version="1.0.0",
    description=(
        "Serverless GenAI orchestrator for real-time FIFA World Cup 2026 "
        "tournament operations. Provides crowd safety evaluation, accessibility-aware "
        "transit routing, supply chain monitoring, and multilingual translation "
        "across 16 host venues in the United States, Canada, and Mexico."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production to specific frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request Logging Middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request timing for latency monitoring."""
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Processing-Time-Ms"] = f"{duration_ms:.2f}"
    return response


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get(
    "/v1/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="System health check",
)
async def health_check():
    """Returns system health status and version information."""
    return HealthResponse()


# ---------------------------------------------------------------------------
# Crowd Safety Evaluation
# ---------------------------------------------------------------------------

@app.post(
    "/v1/ops/evaluate",
    response_model=OperationalResponse,
    tags=["Crowd Safety"],
    summary="Evaluate zone crowd safety metrics",
    description=(
        "Evaluates real-time crowd density and flow metrics against safety "
        "thresholds. Triggers DIM-ICE framework interventions when thresholds "
        "are exceeded (Density > 4.5 pax/m², Flow < 25 pax/m/min)."
    ),
)
async def evaluate_zone_safety(metrics: CrowdMetrics):
    """
    Evaluate real-time crowd safety metrics and generate structured
    operational directives using the DIM-ICE framework.
    """
    try:
        # Use deterministic evaluation (always available, no API dependency)
        result = evaluate_crowd_safety(metrics)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred during operational evaluation. Please retry.",
        )


@app.post(
    "/v1/ops/evaluate/ai",
    response_model=OperationalResponse,
    tags=["Crowd Safety"],
    summary="AI-enhanced zone safety evaluation",
    description=(
        "Enhanced evaluation using the Pydantic AI agent with Gemini 2.0 Flash "
        "for natural-language safety analysis. Falls back to deterministic "
        "evaluation if the AI agent is unavailable."
    ),
)
async def evaluate_zone_safety_ai(metrics: CrowdMetrics):
    """
    AI-enhanced crowd safety evaluation with Gemini-powered reasoning.
    """
    try:
        result = await evaluate_with_agent(metrics)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # Fallback to deterministic on any AI failure
        return evaluate_crowd_safety(metrics)


# ---------------------------------------------------------------------------
# Transit Routing
# ---------------------------------------------------------------------------

@app.post(
    "/v1/ops/transit",
    response_model=TransitResponse,
    tags=["Transit & Accessibility"],
    summary="Accessibility-aware transit routing",
    description=(
        "Generates optimized transit routes with step-free accessibility "
        "options, carbon scoring, and venue-specific recommendations."
    ),
)
async def get_transit_route(request: TransitRequest):
    """
    Generate an accessibility-aware transit route to a venue.
    """
    try:
        return generate_transit_route(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the transit route.",
        )


# ---------------------------------------------------------------------------
# Supply Chain
# ---------------------------------------------------------------------------

@app.post(
    "/v1/ops/supply",
    response_model=SupplyChainResponse,
    tags=["Supply Chain"],
    summary="Supply chain status and alerts",
    description=(
        "Evaluates supply chain status including inventory levels, demand "
        "forecasts, and cold chain temperature monitoring for a venue."
    ),
)
async def get_supply_status(venue_city: str):
    """
    Get supply chain status and alerts for a specific venue.
    """
    try:
        return evaluate_supply_chain(venue_city)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while evaluating supply chain status.",
        )


# ---------------------------------------------------------------------------
# Multilingual Translation
# ---------------------------------------------------------------------------

@app.post(
    "/v1/ops/translate",
    response_model=TranslationResponse,
    tags=["Multilingual"],
    summary="Dynamic multilingual translation",
    description=(
        "Translates safety notices, menu boards, allergen disclosures, "
        "and transportation guides. Pre-translated safety templates are "
        "served instantly; custom text is processed dynamically."
    ),
)
async def translate(request: TranslationRequest):
    """
    Translate text for multilingual fan engagement.
    """
    try:
        return translate_text(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred during translation.",
        )


@app.get(
    "/v1/ops/languages",
    tags=["Multilingual"],
    summary="List supported languages",
)
async def list_languages():
    """Return all supported languages."""
    return get_supported_languages()


# ---------------------------------------------------------------------------
# Venue Data
# ---------------------------------------------------------------------------

@app.get(
    "/v1/venues",
    response_model=list[VenueProfile],
    tags=["Venues"],
    summary="List all 16 host venue profiles",
)
async def list_venues():
    """Return operational profiles for all 16 host city venues."""
    return get_all_venue_profiles()


@app.get(
    "/v1/venues/{city_key}",
    response_model=VenueProfile,
    tags=["Venues"],
    summary="Get specific venue profile",
)
async def get_venue(city_key: str):
    """Return the operational profile for a specific host city."""
    profile = get_venue_profile(city_key)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"Venue '{city_key}' not found. Available: {', '.join(VENUE_PROFILES.keys())}",
        )
    return profile


# ---------------------------------------------------------------------------
# Guardrail-Protected General Query
# ---------------------------------------------------------------------------

@app.post(
    "/v1/ops/query",
    tags=["Operations"],
    summary="General operational query (guardrail-protected)",
    description=(
        "Process a general operational query through the security guardrail "
        "pipeline. Validates input, checks domain relevance, and returns "
        "a sanitized response."
    ),
)
async def operational_query(query: str):
    """
    Process a guardrail-protected operational query.
    """
    # Input sanitization
    guard_result = sanitize_input(query)
    if not guard_result.is_safe:
        raise HTTPException(
            status_code=403,
            detail=f"Security policy violation: {guard_result.threat_detected}",
        )

    # Domain relevance check
    if not check_domain_relevance(query):
        return {
            "response": (
                "I can only assist with FIFA World Cup 2026 stadium operations, "
                "crowd safety, transit management, accessibility, and multilingual "
                "translation. Please rephrase your query within these domains."
            ),
            "domain_relevant": False,
        }

    return {
        "response": (
            "Query accepted. Use specific endpoints for detailed operations: "
            "/v1/ops/evaluate (crowd safety), /v1/ops/transit (routing), "
            "/v1/ops/supply (logistics), /v1/ops/translate (translation)."
        ),
        "domain_relevant": True,
        "processing_time_ms": guard_result.processing_time_ms,
    }


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
