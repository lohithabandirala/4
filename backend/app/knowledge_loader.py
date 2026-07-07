"""
AegisSphere — Knowledge Base Loader
====================================
Loads and serves data from the JSON knowledge base files stored in
the backend/knowledge/ directory. Provides secure, read-only access
to stadium policies, accessibility routes, and venue profiles.
"""

from __future__ import annotations

import json
import os
from typing import Optional

# ---------------------------------------------------------------------------
# Knowledge Base Path
# ---------------------------------------------------------------------------

_KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge")


# ---------------------------------------------------------------------------
# Stadium Policies
# ---------------------------------------------------------------------------

_STADIUM_POLICIES: dict[str, str] = {}


def _load_stadium_policies() -> None:
    """Load stadium policies from JSON file."""
    global _STADIUM_POLICIES
    policy_file = os.path.join(_KNOWLEDGE_DIR, "stadium_policies.json")
    if os.path.exists(policy_file):
        with open(policy_file, "r", encoding="utf-8") as f:
            _STADIUM_POLICIES = json.load(f)
    else:
        # Fallback inline policies
        _STADIUM_POLICIES = {
            "gate_a_concourse": "Evacuation path via Weller Street Bridge. Capacity limit: 5000. Step-free access available.",
            "gate_b_concourse": "Evacuation path via North Plaza. Capacity limit: 4500. Elevator access at Level 2.",
            "south_plaza": "Evacuation path to Parking Lot C. Capacity limit: 12000. Open-air assembly point.",
            "north_plaza": "Evacuation path to Parking Lot A. Capacity limit: 10000. Covered waiting area available.",
            "main_concourse": "Primary circulation route. Capacity limit: 8000. Bidirectional flow management active.",
            "east_concourse": "Secondary circulation route. Capacity limit: 6000. Accessible restrooms at sections 4-6.",
            "west_concourse": "Secondary circulation route. Capacity limit: 5500. Medical station at section 12.",
            "vip_entrance": "Dedicated VIP evacuation via underground tunnel. Capacity limit: 1500.",
            "media_center": "Media evacuation via service corridors. Capacity limit: 2000.",
            "fan_zone_east": "Open-air fan zone. Evacuation to East Parking. Capacity limit: 15000.",
            "fan_zone_west": "Open-air fan zone. Evacuation to West Transit Hub. Capacity limit: 12000.",
        }


def get_stadium_policy(zone_id: str) -> str:
    """
    Retrieve authorized evacuation and routing rules for a specific zone.

    Args:
        zone_id: Stadium zone identifier.

    Returns:
        Policy string for the zone.
    """
    if not _STADIUM_POLICIES:
        _load_stadium_policies()

    return _STADIUM_POLICIES.get(
        zone_id,
        "Use standard stadium exit routes. Follow illuminated exit signage and steward directions."
    )


# ---------------------------------------------------------------------------
# Accessibility Routes
# ---------------------------------------------------------------------------

_ACCESSIBILITY_ROUTES: dict = {}


def _load_accessibility_routes() -> None:
    """Load accessibility route data from JSON file."""
    global _ACCESSIBILITY_ROUTES
    routes_file = os.path.join(_KNOWLEDGE_DIR, "accessibility_routes.json")
    if os.path.exists(routes_file):
        with open(routes_file, "r", encoding="utf-8") as f:
            _ACCESSIBILITY_ROUTES = json.load(f)


def get_accessibility_info(venue_city: str) -> Optional[dict]:
    """Get accessibility information for a venue."""
    if not _ACCESSIBILITY_ROUTES:
        _load_accessibility_routes()
    return _ACCESSIBILITY_ROUTES.get(venue_city.lower().replace(" ", "_"))


# ---------------------------------------------------------------------------
# FAA No Drone Zones
# ---------------------------------------------------------------------------

_FAA_ZONES: dict = {}


def _load_faa_zones() -> None:
    """Load FAA no-drone zone data."""
    global _FAA_ZONES
    faa_file = os.path.join(_KNOWLEDGE_DIR, "faa_no_drone_zones.json")
    if os.path.exists(faa_file):
        with open(faa_file, "r", encoding="utf-8") as f:
            _FAA_ZONES = json.load(f)


def get_faa_restriction(venue_city: str) -> Optional[str]:
    """Get FAA drone restriction for a US venue."""
    if not _FAA_ZONES:
        _load_faa_zones()
    zone = _FAA_ZONES.get(venue_city.lower().replace(" ", "_"))
    if zone:
        return zone.get("restriction")
    return None
