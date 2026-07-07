"""
AegisSphere — Accessibility-Aware Transit Routing
==================================================
Provides optimized, step-free transit routes for mobility-impaired fans
and green transport alternatives for all attendees.

Key features:
    - Step-free routing with venue-specific accessible pathways
    - Seattle Lumen Field: Weller Street Bridge over Pioneer Square
    - Cross-jurisdictional routing (MetLife Stadium: NJ + NY)
    - Carbon scoring for sustainable transport incentives
    - FAA No Drone Zone enforcement
"""

from __future__ import annotations

from typing import Optional
import uuid

from app.schemas import (
    TransitRequest,
    TransitResponse,
    TransitStep,
    TransportMode,
    VenueProfile,
)
from app.venue_data import get_venue_profile


# ---------------------------------------------------------------------------
# Venue-Specific Accessible Routes
# ---------------------------------------------------------------------------

# Pre-computed accessibility routes per venue
_ACCESSIBLE_ROUTES: dict[str, dict] = {
    "seattle": {
        "default_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.LIGHT_RAIL,
                    instruction="Take Sound Transit Link Light Rail to Stadium Station",
                    duration_minutes=12.0,
                    is_step_free=True,
                    accessibility_notes="Level boarding at all platforms",
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction=(
                        "Exit at Weller Street Bridge station for a level, step-free pathway. "
                        "AVOID Pioneer Square — steep grades and crowded walkways are not accessible."
                    ),
                    duration_minutes=8.0,
                    is_step_free=True,
                    accessibility_notes="Weller Street Bridge provides flat, wide pathway to Lumen Field",
                ),
            ],
            "warnings": [
                "Pioneer Square route is NOT recommended for reduced-mobility passengers due to steep grades.",
                "Concourse pinch points may cause delays — follow steward directions for accessible gates.",
            ],
        },
        "standard_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.LIGHT_RAIL,
                    instruction="Take Sound Transit Link Light Rail to Stadium Station",
                    duration_minutes=12.0,
                    is_step_free=True,
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Walk south through Pioneer Square to Lumen Field main entrance",
                    duration_minutes=6.0,
                    is_step_free=False,
                    accessibility_notes="Steep grades — not suitable for wheelchair users",
                ),
            ],
            "warnings": [],
        },
    },
    "new_york_nj": {
        "default_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.RAIL,
                    instruction="Take NJ Transit Meadowlands Rail from Secaucus Junction to MetLife Stadium",
                    duration_minutes=15.0,
                    is_step_free=True,
                    accessibility_notes="Accessible platform with gap ramps at Secaucus Junction",
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Follow accessible pathway from rail platform to Gate A (level, covered walkway)",
                    duration_minutes=5.0,
                    is_step_free=True,
                    accessibility_notes="Covered walkway with tactile paving for visually impaired fans",
                ),
            ],
            "warnings": [
                "Cross-jurisdictional travel: NJ Transit and MTA tickets are separate systems.",
                "Post-match rail capacity is limited — expect 30-45 minute waits during peak egress.",
            ],
        },
        "standard_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.BUS,
                    instruction="Take NJ Transit Bus 160/165 from Port Authority to MetLife Stadium",
                    duration_minutes=25.0,
                    is_step_free=True,
                ),
            ],
            "warnings": [
                "Bus service may be suspended during peak match-day periods."
            ],
        },
    },
    "dallas": {
        "default_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.SHUTTLE,
                    instruction="Take DART Park-and-Ride shuttle from CentrePort/DFW Station to AT&T Stadium",
                    duration_minutes=20.0,
                    is_step_free=True,
                    accessibility_notes="Wheelchair-accessible shuttle with A/C — critical in heat conditions",
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Follow shaded accessible pathway from shuttle drop-off to Gate D",
                    duration_minutes=5.0,
                    is_step_free=True,
                    accessibility_notes="Shaded pathway with hydration stations",
                ),
            ],
            "warnings": [
                "HEAT ADVISORY: Temperatures may exceed 100°F. Use air-conditioned shuttles.",
                "Limited public transit — park-and-ride is the primary option.",
            ],
        },
        "standard_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.RIDESHARE,
                    instruction="Rideshare drop-off at Lot 4 designated zone",
                    duration_minutes=15.0,
                    is_step_free=True,
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Walk from Lot 4 to stadium entrance (partial sun exposure)",
                    duration_minutes=10.0,
                    is_step_free=False,
                ),
            ],
            "warnings": [
                "HEAT ADVISORY: Carry water and use provided shade structures.",
            ],
        },
    },
    "miami": {
        "default_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.SHUTTLE,
                    instruction="Take FIFA Express Shuttle from Aventura Mall to Hard Rock Stadium",
                    duration_minutes=15.0,
                    is_step_free=True,
                    accessibility_notes="Climate-controlled accessible shuttle",
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Follow covered pathway to accessible entrance at Gate G",
                    duration_minutes=3.0,
                    is_step_free=True,
                ),
            ],
            "warnings": [
                "TROPICAL WEATHER: Monitor flash flood warnings — evacuation routes may change.",
                "No light rail service to Hard Rock Stadium.",
            ],
        },
        "standard_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.RIDESHARE,
                    instruction="Rideshare to Hard Rock Stadium north entrance",
                    duration_minutes=20.0,
                    is_step_free=True,
                ),
            ],
            "warnings": [
                "Extreme airport surge expected — allow extra travel time from MIA.",
            ],
        },
    },
    "atlanta": {
        "default_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.RAIL,
                    instruction="Take MARTA Blue/Green Line to Vine City Station",
                    duration_minutes=10.0,
                    is_step_free=True,
                    accessibility_notes="Elevator access at Vine City Station",
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Follow accessible bridge walkway to Mercedes-Benz Stadium Gate 1",
                    duration_minutes=7.0,
                    is_step_free=True,
                    accessibility_notes="Level bridge with non-slip surface",
                ),
            ],
            "warnings": [
                "MARTA central hub congestion expected — consider off-peak arrival.",
            ],
        },
        "standard_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.RAIL,
                    instruction="Take MARTA to GWCC/CNN Center Station (closer but more crowded)",
                    duration_minutes=8.0,
                    is_step_free=True,
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Walk through Centennial Olympic Park to stadium",
                    duration_minutes=10.0,
                    is_step_free=False,
                    accessibility_notes="Some uneven surfaces in park area",
                ),
            ],
            "warnings": [],
        },
    },
    "mexico_city": {
        "default_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.LIGHT_RAIL,
                    instruction="Take Metro Línea 2 to Tasqueña, then Tren Ligero to Estadio Azteca",
                    duration_minutes=25.0,
                    is_step_free=False,
                    accessibility_notes="Limited elevator access at some stations — assistance available",
                ),
                TransitStep(
                    mode=TransportMode.ACCESSIBLE_SHUTTLE,
                    instruction="Take FIFA accessible shuttle from Tren Ligero stop to Estadio Azteca Gate B",
                    duration_minutes=5.0,
                    is_step_free=True,
                    accessibility_notes="Wheelchair ramp equipped shuttle",
                ),
            ],
            "warnings": [
                "HIGH ALTITUDE: Estadio Azteca is at 2,200m elevation. Take breaks and stay hydrated.",
                "Summer rain expected — bring rain gear for outdoor queuing.",
            ],
        },
        "standard_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.LIGHT_RAIL,
                    instruction="Take Metro Línea 2 to Tasqueña, then Tren Ligero to Estadio Azteca",
                    duration_minutes=25.0,
                    is_step_free=False,
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Walk uphill from Tren Ligero platform to stadium entrance",
                    duration_minutes=10.0,
                    is_step_free=False,
                ),
            ],
            "warnings": [
                "HIGH ALTITUDE WARNING: Walking uphill at 2,200m may cause shortness of breath.",
            ],
        },
    },
    "vancouver": {
        "default_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.LIGHT_RAIL,
                    instruction="Take SkyTrain Expo/Millennium Line to Stadium-Chinatown Station",
                    duration_minutes=10.0,
                    is_step_free=True,
                    accessibility_notes="All SkyTrain stations have elevator access",
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Follow accessible pathway from station to BC Place Gate A",
                    duration_minutes=5.0,
                    is_step_free=True,
                    accessibility_notes="Flat, wide pathway with tactile guiding strips",
                ),
            ],
            "warnings": [
                "AIR QUALITY: Check wildfire smoke index before travelling — masks recommended if AQI > 150.",
            ],
        },
        "standard_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.LIGHT_RAIL,
                    instruction="Take SkyTrain to Stadium-Chinatown Station",
                    duration_minutes=10.0,
                    is_step_free=True,
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Walk to BC Place main entrance",
                    duration_minutes=4.0,
                    is_step_free=True,
                ),
            ],
            "warnings": [],
        },
    },
    "toronto": {
        "default_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.STREETCAR,
                    instruction="Take TTC Streetcar 509 (Harbourfront) to Exhibition Loop",
                    duration_minutes=15.0,
                    is_step_free=True,
                    accessibility_notes="Low-floor streetcar with wheelchair ramp",
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Follow lakeside accessible path to BMO Field entrance",
                    duration_minutes=5.0,
                    is_step_free=True,
                    accessibility_notes="Flat lakeside path — avoid Liberty Village shortcut (stairs)",
                ),
            ],
            "warnings": [
                "Lakeside streetcar congestion expected — allow extra 15 minutes during match windows.",
            ],
        },
        "standard_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.STREETCAR,
                    instruction="Take TTC Streetcar 509 to Exhibition Loop",
                    duration_minutes=15.0,
                    is_step_free=True,
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Walk through Exhibition Place to BMO Field",
                    duration_minutes=8.0,
                    is_step_free=True,
                ),
            ],
            "warnings": [],
        },
    },
    "boston": {
        "default_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.RAIL,
                    instruction="Take MBTA Commuter Rail (Franklin/Foxboro Line) to Foxborough",
                    duration_minutes=45.0,
                    is_step_free=False,
                    accessibility_notes="Request accessible car — single-track may cause delays",
                ),
                TransitStep(
                    mode=TransportMode.SHUTTLE,
                    instruction="Take FIFA accessible shuttle from Foxborough station to Gillette Stadium",
                    duration_minutes=5.0,
                    is_step_free=True,
                    accessibility_notes="Wheelchair-accessible shuttle",
                ),
            ],
            "warnings": [
                "Single-track commuter rail: Delays likely post-match. Plan for extended wait times.",
                "Post-match embarkation scheduling required — check app for assigned departure slot.",
            ],
        },
        "standard_route": {
            "steps": [
                TransitStep(
                    mode=TransportMode.RAIL,
                    instruction="Take MBTA Commuter Rail to Foxborough",
                    duration_minutes=45.0,
                    is_step_free=False,
                ),
                TransitStep(
                    mode=TransportMode.WALKING,
                    instruction="Walk from Foxborough station to Gillette Stadium",
                    duration_minutes=10.0,
                    is_step_free=False,
                ),
            ],
            "warnings": [],
        },
    },
}

# Default generic route for venues without specific data
_DEFAULT_GENERIC_ROUTE = {
    "steps": [
        TransitStep(
            mode=TransportMode.SHUTTLE,
            instruction="Take the FIFA World Cup Shuttle from the nearest transit hub to the venue",
            duration_minutes=15.0,
            is_step_free=True,
            accessibility_notes="Wheelchair-accessible shuttle available",
        ),
    ],
    "warnings": ["Check the AegisSphere app for real-time transit updates and route changes."],
}


# ---------------------------------------------------------------------------
# Carbon Scoring
# ---------------------------------------------------------------------------

_CARBON_SCORES: dict[TransportMode, float] = {
    TransportMode.WALKING: 100.0,       # Zero carbon
    TransportMode.RAIL: 90.0,           # Electric rail
    TransportMode.LIGHT_RAIL: 90.0,     # Electric light rail
    TransportMode.STREETCAR: 85.0,      # Electric streetcar
    TransportMode.BUS: 65.0,            # Diesel/hybrid bus
    TransportMode.SHUTTLE: 60.0,        # Shuttle bus
    TransportMode.ACCESSIBLE_SHUTTLE: 60.0,
    TransportMode.RIDESHARE: 30.0,      # Single-occupancy vehicle
}


def _calculate_carbon_score(steps: list[TransitStep]) -> float:
    """Calculate weighted carbon score for a multi-modal route."""
    if not steps:
        return 0.0

    total_duration = sum(s.duration_minutes for s in steps)
    if total_duration == 0:
        return 0.0

    weighted_score = sum(
        _CARBON_SCORES.get(s.mode, 50.0) * s.duration_minutes
        for s in steps
    )
    return round(weighted_score / total_duration, 1)


# ---------------------------------------------------------------------------
# FAA No Drone Zone Enforcement
# ---------------------------------------------------------------------------

_NO_DRONE_ZONES: dict[str, dict] = {
    "los_angeles": {"radius_km": 5.6, "restriction": "NSSE TFR — No UAS operations within 5.6km of SoFi Stadium"},
    "dallas": {"radius_km": 5.6, "restriction": "NSSE TFR — No UAS operations within 5.6km of AT&T Stadium"},
    "houston": {"radius_km": 5.6, "restriction": "NSSE TFR — No UAS operations within 5.6km of NRG Stadium"},
    "miami": {"radius_km": 5.6, "restriction": "NSSE TFR — No UAS operations within 5.6km of Hard Rock Stadium"},
    "seattle": {"radius_km": 5.6, "restriction": "NSSE TFR — No UAS operations within 5.6km of Lumen Field"},
    "new_york_nj": {"radius_km": 5.6, "restriction": "NSSE TFR — No UAS operations within 5.6km of MetLife Stadium"},
    "atlanta": {"radius_km": 5.6, "restriction": "NSSE TFR — No UAS operations within 5.6km of Mercedes-Benz Stadium"},
    "boston": {"radius_km": 5.6, "restriction": "NSSE TFR — No UAS operations within 5.6km of Gillette Stadium"},
    "philadelphia": {"radius_km": 5.6, "restriction": "NSSE TFR — No UAS operations within 5.6km of Lincoln Financial Field"},
    "kansas_city": {"radius_km": 5.6, "restriction": "NSSE TFR — No UAS operations within 5.6km of Arrowhead Stadium"},
    "san_francisco": {"radius_km": 5.6, "restriction": "NSSE TFR — No UAS operations within 5.6km of Levi's Stadium"},
}


def check_drone_zone(city_key: str) -> Optional[str]:
    """Check if a venue has FAA No Drone Zone restrictions."""
    zone = _NO_DRONE_ZONES.get(city_key.lower().replace(" ", "_"))
    if zone:
        return zone["restriction"]
    return None


# ---------------------------------------------------------------------------
# Route Generation
# ---------------------------------------------------------------------------

def generate_transit_route(request: TransitRequest) -> TransitResponse:
    """
    Generate an accessibility-aware transit route for a specific venue.

    Selects the appropriate route variant based on accessibility requirements
    and applies carbon scoring for sustainable transport incentives.

    Args:
        request: Transit routing request with origin, destination, and preferences.

    Returns:
        Complete TransitResponse with step-by-step directions and metadata.
    """
    city_key = request.venue_city.lower().replace(" ", "_").replace("/", "_")
    venue_routes = _ACCESSIBLE_ROUTES.get(city_key, None)

    if venue_routes is None:
        # Fall back to generic route
        route_data = _DEFAULT_GENERIC_ROUTE
    elif request.require_step_free:
        route_data = venue_routes.get("default_route", _DEFAULT_GENERIC_ROUTE)
    else:
        route_data = venue_routes.get("standard_route", venue_routes.get("default_route", _DEFAULT_GENERIC_ROUTE))

    steps = route_data["steps"]
    warnings = route_data.get("warnings", [])

    # Check FAA drone zone and add warning if applicable
    drone_warning = check_drone_zone(city_key)
    if drone_warning:
        warnings = warnings + [f"🚁 {drone_warning}"]

    total_duration = sum(s.duration_minutes for s in steps)
    is_fully_accessible = all(s.is_step_free for s in steps)
    carbon_score = _calculate_carbon_score(steps)

    return TransitResponse(
        route_id=f"RT-{uuid.uuid4().hex[:8].upper()}",
        origin=request.origin,
        destination=request.destination,
        total_duration_minutes=total_duration,
        is_fully_accessible=is_fully_accessible,
        carbon_score=carbon_score,
        steps=steps,
        warnings=warnings if warnings else None,
    )
