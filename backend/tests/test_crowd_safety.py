"""
AegisSphere — Crowd Safety Unit Tests
======================================
Unit tests for the DIM-ICE crowd safety engine, including density/flow
computation, threshold evaluation, classification, and intervention
generation.
"""

import pytest

from app.crowd_safety import (
    compute_density,
    compute_flow,
    evaluate_safety,
    classify_dim_ice,
    generate_intervention,
    evaluate_crowd_safety,
    determine_incident_phase,
    DENSITY_THRESHOLD,
    FLOW_THRESHOLD,
    AMBER_DENSITY_THRESHOLD,
    AMBER_FLOW_THRESHOLD,
)
from app.schemas import (
    CrowdMetrics,
    DIMICECategory,
    EscalationCode,
    IncidentPhase,
)


# ---------------------------------------------------------------------------
# Density Computation Tests
# ---------------------------------------------------------------------------

class TestComputeDensity:
    def test_normal_density(self):
        """100 people in 50 m² = 2.0 persons/m²"""
        assert compute_density(100, 50.0) == 2.0

    def test_high_density(self):
        """500 people in 100 m² = 5.0 persons/m²"""
        assert compute_density(500, 100.0) == 5.0

    def test_zero_persons(self):
        """0 people = 0.0 density"""
        assert compute_density(0, 100.0) == 0.0

    def test_zero_area_raises(self):
        """Zero area should raise ValueError"""
        with pytest.raises(ValueError, match="Area must be positive"):
            compute_density(100, 0.0)

    def test_negative_area_raises(self):
        """Negative area should raise ValueError"""
        with pytest.raises(ValueError, match="Area must be positive"):
            compute_density(100, -10.0)


# ---------------------------------------------------------------------------
# Flow Computation Tests
# ---------------------------------------------------------------------------

class TestComputeFlow:
    def test_normal_flow(self):
        """100 people through 2m passage in 1 min = 50 p/m/min"""
        assert compute_flow(100, 2.0, 1.0) == 50.0

    def test_low_flow(self):
        """50 people through 5m passage in 2 min = 5 p/m/min"""
        assert compute_flow(50, 5.0, 2.0) == 5.0

    def test_zero_width_raises(self):
        """Zero width should raise ValueError"""
        with pytest.raises(ValueError, match="Width must be positive"):
            compute_flow(100, 0.0, 1.0)

    def test_zero_duration_raises(self):
        """Zero duration should raise ValueError"""
        with pytest.raises(ValueError, match="Duration must be positive"):
            compute_flow(100, 2.0, 0.0)


# ---------------------------------------------------------------------------
# Safety Evaluation Tests
# ---------------------------------------------------------------------------

class TestEvaluateSafety:
    def test_green_nominal(self):
        """Low density and high flow = GREEN"""
        verdict = evaluate_safety(1.5, 40.0)
        assert verdict.escalation_code == EscalationCode.GREEN
        assert verdict.is_critical is False
        assert verdict.is_warning is False

    def test_red_critical(self):
        """High density AND low flow = RED (both thresholds exceeded)"""
        verdict = evaluate_safety(5.0, 20.0)
        assert verdict.escalation_code == EscalationCode.RED
        assert verdict.is_critical is True
        assert verdict.density_exceeded is True
        assert verdict.flow_exceeded is True

    def test_amber_high_density_only(self):
        """High density but normal flow = AMBER (not RED)"""
        verdict = evaluate_safety(4.0, 40.0)
        assert verdict.escalation_code == EscalationCode.AMBER
        assert verdict.is_critical is False
        assert verdict.is_warning is True

    def test_amber_low_flow_only(self):
        """Normal density but approaching low flow = AMBER"""
        verdict = evaluate_safety(2.0, 30.0)
        assert verdict.escalation_code == EscalationCode.AMBER
        assert verdict.is_critical is False
        assert verdict.is_warning is True

    def test_boundary_exact_threshold(self):
        """Exactly at threshold = not exceeded (strict inequality)"""
        verdict = evaluate_safety(DENSITY_THRESHOLD, FLOW_THRESHOLD)
        # At exactly 4.5 and 25, neither threshold is exceeded
        assert verdict.is_critical is False

    def test_boundary_just_above_threshold(self):
        """Just above density threshold and just below flow = RED"""
        verdict = evaluate_safety(4.51, 24.99)
        assert verdict.escalation_code == EscalationCode.RED
        assert verdict.is_critical is True


# ---------------------------------------------------------------------------
# DIM-ICE Classification Tests
# ---------------------------------------------------------------------------

class TestClassifyDIMICE:
    def test_design_concourse(self):
        """Concourse zones = Design classification"""
        category = classify_dim_ice("gate_a_concourse", 5.0, 10.0)
        assert category == DIMICECategory.DESIGN

    def test_design_tunnel(self):
        """Tunnel zones = Design classification"""
        category = classify_dim_ice("access_tunnel_north", 5.0, 10.0)
        assert category == DIMICECategory.DESIGN

    def test_information_plaza(self):
        """Plaza zones = Information classification"""
        category = classify_dim_ice("south_plaza", 4.0, 30.0)
        assert category == DIMICECategory.INFORMATION

    def test_information_fan_zone(self):
        """Fan zone = Information classification"""
        category = classify_dim_ice("fan_zone_east", 3.5, 28.0)
        assert category == DIMICECategory.INFORMATION

    def test_management_low_staffing(self):
        """Low staffing ratio = Management classification"""
        category = classify_dim_ice("open_area", 4.0, 30.0, staffing_ratio=0.001)
        assert category == DIMICECategory.MANAGEMENT

    def test_design_extreme_conditions(self):
        """Very high density + very low flow = Design (even in unknown zones)"""
        category = classify_dim_ice("unknown_zone", 6.0, 10.0)
        assert category == DIMICECategory.DESIGN


# ---------------------------------------------------------------------------
# Incident Phase Tests
# ---------------------------------------------------------------------------

class TestDetermineIncidentPhase:
    def test_ingress_gate(self):
        assert determine_incident_phase("main_gate_entrance") == IncidentPhase.INGRESS

    def test_ingress_turnstile(self):
        assert determine_incident_phase("turnstile_north") == IncidentPhase.INGRESS

    def test_egress_exit(self):
        assert determine_incident_phase("emergency_exit_south") == IncidentPhase.EGRESS

    def test_egress_parking(self):
        assert determine_incident_phase("parking_lot_b") == IncidentPhase.EGRESS

    def test_circulation_concourse(self):
        assert determine_incident_phase("main_concourse") == IncidentPhase.CIRCULATION

    def test_circulation_default(self):
        assert determine_incident_phase("random_zone") == IncidentPhase.CIRCULATION


# ---------------------------------------------------------------------------
# Intervention Generation Tests
# ---------------------------------------------------------------------------

class TestGenerateIntervention:
    def test_design_intervention(self):
        """Design intervention should dispatch staff and suggest rerouting"""
        action = generate_intervention(
            DIMICECategory.DESIGN, "gate_a_concourse", 5.2, 12.0, EscalationCode.RED
        )
        assert action.action_type == DIMICECategory.DESIGN
        assert action.dispatch_staff is True
        assert action.escalation_code == EscalationCode.RED
        assert "gate_a_concourse" in action.broadcast_message
        assert action.reroute_zones is not None

    def test_information_intervention(self):
        """Information intervention should address signage"""
        action = generate_intervention(
            DIMICECategory.INFORMATION, "south_plaza", 4.0, 20.0, EscalationCode.AMBER
        )
        assert action.action_type == DIMICECategory.INFORMATION
        assert "signage" in action.broadcast_message.lower() or "wayfinding" in action.broadcast_message.lower()

    def test_management_intervention(self):
        """Management intervention should deploy stewards"""
        action = generate_intervention(
            DIMICECategory.MANAGEMENT, "north_plaza", 5.0, 15.0, EscalationCode.RED
        )
        assert action.action_type == DIMICECategory.MANAGEMENT
        assert action.dispatch_staff is True
        assert "steward" in action.broadcast_message.lower()


# ---------------------------------------------------------------------------
# Full Pipeline Tests
# ---------------------------------------------------------------------------

class TestEvaluateCrowdSafety:
    def test_full_pipeline_nominal(self):
        """Full pipeline with safe metrics returns NOMINAL"""
        metrics = CrowdMetrics(density=1.0, flow=50.0, zone_id="south_plaza")
        result = evaluate_crowd_safety(metrics)
        assert result.incident_detected is False
        assert result.system_status == "NOMINAL"
        assert result.recommended_action is None

    def test_full_pipeline_critical(self):
        """Full pipeline with critical metrics returns ALERT with action"""
        metrics = CrowdMetrics(density=5.5, flow=10.0, zone_id="gate_a_concourse")
        result = evaluate_crowd_safety(metrics)
        assert result.incident_detected is True
        assert result.system_status == "ALERT"
        assert result.recommended_action is not None
        assert result.recommended_action.escalation_code == EscalationCode.RED

    def test_full_pipeline_warning(self):
        """Full pipeline with warning-level metrics returns WARNING"""
        metrics = CrowdMetrics(density=4.0, flow=30.0, zone_id="main_concourse")
        result = evaluate_crowd_safety(metrics)
        assert result.incident_detected is False
        assert result.system_status == "WARNING"
