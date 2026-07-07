"""
AegisSphere — Crowd Safety Engine (DIM-ICE Framework)
=====================================================
Real-time crowd dynamics computation and safety intervention logic.
Implements the DIM-ICE (Design, Information, Management — Ingress,
Circulation, Egress) framework for automated bottleneck detection
and remediation.

Safety Thresholds (per crowd dynamics research):
    - Density trigger:  D > 4.5 persons/m²
    - Flow trigger:     F < 25 persons/m/min
    - Combined trigger: BOTH conditions must be true for RED escalation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.schemas import (
    CrowdMetrics,
    DIMICECategory,
    EmergencyAction,
    EscalationCode,
    IncidentPhase,
    OperationalResponse,
)

# ---------------------------------------------------------------------------
# Safety Threshold Constants
# ---------------------------------------------------------------------------

DENSITY_THRESHOLD: float = 4.5       # persons per square meter
FLOW_THRESHOLD: float = 25.0         # persons per meter per minute
AMBER_DENSITY_THRESHOLD: float = 3.5  # early-warning density
AMBER_FLOW_THRESHOLD: float = 35.0    # early-warning flow rate


# ---------------------------------------------------------------------------
# Core Computations
# ---------------------------------------------------------------------------

def compute_density(n_persons: int, area_m2: float) -> float:
    """
    Calculate localized zone density.

    D = N / A  (persons/m²)

    Args:
        n_persons: Number of individuals present in the zone.
        area_m2: Area of the zone in square meters.

    Returns:
        Crowd density in persons per square meter.

    Raises:
        ValueError: If area_m2 is zero or negative.
    """
    if area_m2 <= 0:
        raise ValueError(f"Area must be positive, got {area_m2}")
    return n_persons / area_m2


def compute_flow(n_persons: int, width_m: float, duration_min: float) -> float:
    """
    Calculate pedestrian flow rate.

    F = N / (W · t)  (persons/m/min)

    Args:
        n_persons: Number of individuals crossing the threshold.
        width_m: Effective passage width in meters.
        duration_min: Elapsed duration in minutes.

    Returns:
        Pedestrian flow rate in persons per meter per minute.

    Raises:
        ValueError: If width_m or duration_min is zero or negative.
    """
    if width_m <= 0:
        raise ValueError(f"Width must be positive, got {width_m}")
    if duration_min <= 0:
        raise ValueError(f"Duration must be positive, got {duration_min}")
    return n_persons / (width_m * duration_min)


# ---------------------------------------------------------------------------
# Safety Evaluation
# ---------------------------------------------------------------------------

@dataclass
class SafetyVerdict:
    """Result of a crowd safety threshold evaluation."""
    is_critical: bool
    is_warning: bool
    escalation_code: EscalationCode
    density: float
    flow: float
    density_exceeded: bool
    flow_exceeded: bool


def evaluate_safety(density: float, flow: float) -> SafetyVerdict:
    """
    Evaluate crowd metrics against safety thresholds.

    RED:   D > 4.5 AND F < 25  (critical — immediate intervention)
    AMBER: D > 3.5 OR  F < 35  (warning — heightened monitoring)
    GREEN: Otherwise            (nominal — safe flow)

    Args:
        density: Current crowd density (persons/m²).
        flow: Current pedestrian flow rate (persons/m/min).

    Returns:
        SafetyVerdict with escalation classification.
    """
    density_critical = density > DENSITY_THRESHOLD
    flow_critical = flow < FLOW_THRESHOLD
    is_critical = density_critical and flow_critical

    density_warning = density > AMBER_DENSITY_THRESHOLD
    flow_warning = flow < AMBER_FLOW_THRESHOLD
    is_warning = (density_warning or flow_warning) and not is_critical

    if is_critical:
        code = EscalationCode.RED
    elif is_warning:
        code = EscalationCode.AMBER
    else:
        code = EscalationCode.GREEN

    return SafetyVerdict(
        is_critical=is_critical,
        is_warning=is_warning,
        escalation_code=code,
        density=density,
        flow=flow,
        density_exceeded=density_critical,
        flow_exceeded=flow_critical,
    )


# ---------------------------------------------------------------------------
# DIM-ICE Classification
# ---------------------------------------------------------------------------

# Zone patterns that indicate spatial design constraints
DESIGN_ZONE_PATTERNS = [
    "concourse", "tunnel", "bridge", "ramp", "stairway",
    "gate", "entrance", "exit", "corridor",
]

# Zone patterns indicating information / signage issues
INFORMATION_ZONE_PATTERNS = [
    "plaza", "lobby", "atrium", "food_court", "fan_zone",
    "merchandise", "information",
]


def classify_dim_ice(
    zone_id: str,
    density: float,
    flow: float,
    staffing_ratio: Optional[float] = None,
) -> DIMICECategory:
    """
    Classify a crowd bottleneck using the DIM-ICE framework.

    - Design:      Architectural constraints (narrow passages, poor layout)
    - Information:  Unclear signage, missing multilingual instructions
    - Management:   Insufficient staffing or steward deployment

    Args:
        zone_id: Identifier of the affected zone.
        density: Current density in the zone.
        flow: Current flow rate in the zone.
        staffing_ratio: Optional staff-to-crowd ratio (if available).

    Returns:
        The most likely DIM-ICE category for the bottleneck.
    """
    zone_lower = zone_id.lower()

    # Check if the zone matches spatial / design constraint patterns
    if any(pattern in zone_lower for pattern in DESIGN_ZONE_PATTERNS):
        return DIMICECategory.DESIGN

    # If staffing data is available and low, it's a management issue
    if staffing_ratio is not None and staffing_ratio < 0.002:  # < 2 staff per 1000 pax
        return DIMICECategory.MANAGEMENT

    # High density in open areas suggests unclear wayfinding / signage
    if any(pattern in zone_lower for pattern in INFORMATION_ZONE_PATTERNS):
        return DIMICECategory.INFORMATION

    # Default: if density is very high in constrained flow, assume design
    if density > DENSITY_THRESHOLD and flow < FLOW_THRESHOLD * 0.5:
        return DIMICECategory.DESIGN

    return DIMICECategory.MANAGEMENT


def determine_incident_phase(zone_id: str) -> IncidentPhase:
    """
    Determine the DIM-ICE movement phase based on zone type.

    Args:
        zone_id: Identifier of the affected zone.

    Returns:
        The movement phase (Ingress, Circulation, or Egress).
    """
    zone_lower = zone_id.lower()
    ingress_keywords = ["entrance", "gate", "turnstile", "arrival", "ingress"]
    egress_keywords = ["exit", "departure", "egress", "parking", "transit"]

    if any(kw in zone_lower for kw in ingress_keywords):
        return IncidentPhase.INGRESS
    if any(kw in zone_lower for kw in egress_keywords):
        return IncidentPhase.EGRESS
    return IncidentPhase.CIRCULATION


# ---------------------------------------------------------------------------
# Intervention Generation
# ---------------------------------------------------------------------------

# Pre-defined response playbooks per DIM-ICE category
_PLAYBOOKS: dict[DIMICECategory, dict] = {
    DIMICECategory.DESIGN: {
        "dispatch_staff": True,
        "message_template": (
            "⚠️ CROWD ALERT — Zone {zone}: Architectural bottleneck detected. "
            "Please follow steward directions to alternate routes. "
            "Density: {density:.1f} p/m², Flow: {flow:.1f} p/m/min."
        ),
        "reroute": True,
    },
    DIMICECategory.INFORMATION: {
        "dispatch_staff": True,
        "message_template": (
            "ℹ️ WAYFINDING UPDATE — Zone {zone}: Please check updated digital signage "
            "for alternate concession and facility locations. "
            "Current area is experiencing high foot traffic."
        ),
        "reroute": False,
    },
    DIMICECategory.MANAGEMENT: {
        "dispatch_staff": True,
        "message_template": (
            "🚨 SAFETY NOTICE — Zone {zone}: Additional stewards are being deployed. "
            "Please remain calm and follow staff instructions. "
            "Density: {density:.1f} p/m², Flow: {flow:.1f} p/m/min."
        ),
        "reroute": True,
    },
}

# Suggested reroute targets for common zone types
_REROUTE_ZONES: dict[str, list[str]] = {
    "gate_a_concourse": ["gate_b_concourse", "south_plaza"],
    "gate_b_concourse": ["gate_a_concourse", "north_plaza"],
    "south_plaza": ["east_concourse", "parking_lot_c"],
    "north_plaza": ["west_concourse", "parking_lot_a"],
    "main_concourse": ["gate_a_concourse", "gate_b_concourse"],
}


def generate_intervention(
    category: DIMICECategory,
    zone_id: str,
    density: float,
    flow: float,
    escalation: EscalationCode,
) -> EmergencyAction:
    """
    Generate a structured emergency action based on DIM-ICE classification.

    Args:
        category: DIM-ICE classification of the bottleneck.
        zone_id: Affected zone identifier.
        density: Current density reading.
        flow: Current flow reading.
        escalation: Severity code.

    Returns:
        Fully populated EmergencyAction directive.
    """
    playbook = _PLAYBOOKS[category]
    phase = determine_incident_phase(zone_id)

    message = playbook["message_template"].format(
        zone=zone_id,
        density=density,
        flow=flow,
    )

    reroute_zones = None
    if playbook["reroute"]:
        reroute_zones = _REROUTE_ZONES.get(zone_id, ["nearest_available_zone"])

    return EmergencyAction(
        action_type=category,
        phase=phase,
        dispatch_staff=playbook["dispatch_staff"],
        broadcast_message=message,
        escalation_code=escalation,
        reroute_zones=reroute_zones,
    )


# ---------------------------------------------------------------------------
# High-Level Evaluation Pipeline
# ---------------------------------------------------------------------------

def evaluate_crowd_safety(metrics: CrowdMetrics) -> OperationalResponse:
    """
    Full crowd safety evaluation pipeline.

    1. Evaluate density and flow against thresholds.
    2. If thresholds violated, classify via DIM-ICE.
    3. Generate structured intervention if needed.

    Args:
        metrics: Real-time crowd metrics for a zone.

    Returns:
        Complete OperationalResponse with safety analysis and actions.
    """
    verdict = evaluate_safety(metrics.density, metrics.flow)

    if verdict.is_critical:
        category = classify_dim_ice(metrics.zone_id, metrics.density, metrics.flow)
        action = generate_intervention(
            category=category,
            zone_id=metrics.zone_id,
            density=metrics.density,
            flow=metrics.flow,
            escalation=EscalationCode.RED,
        )
        return OperationalResponse(
            incident_detected=True,
            safety_analysis=(
                f"CRITICAL: Zone '{metrics.zone_id}' has exceeded safety thresholds. "
                f"Density = {metrics.density:.1f} persons/m² (threshold: {DENSITY_THRESHOLD}), "
                f"Flow = {metrics.flow:.1f} persons/m/min (threshold: {FLOW_THRESHOLD}). "
                f"DIM-ICE Classification: {category.value}. "
                f"Immediate intervention required."
            ),
            recommended_action=action,
            system_status="ALERT",
        )
    elif verdict.is_warning:
        return OperationalResponse(
            incident_detected=False,
            safety_analysis=(
                f"WARNING: Zone '{metrics.zone_id}' is approaching safety thresholds. "
                f"Density = {metrics.density:.1f} persons/m², "
                f"Flow = {metrics.flow:.1f} persons/m/min. "
                f"Heightened monitoring active."
            ),
            recommended_action=None,
            system_status="WARNING",
        )
    else:
        return OperationalResponse(
            incident_detected=False,
            safety_analysis=(
                f"NOMINAL: Zone '{metrics.zone_id}' is operating within safe parameters. "
                f"Density = {metrics.density:.1f} persons/m², "
                f"Flow = {metrics.flow:.1f} persons/m/min."
            ),
            recommended_action=None,
            system_status="NOMINAL",
        )
