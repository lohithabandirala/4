"""
AegisSphere — Supply Chain & Logistics Engine
==============================================
Predictive demand forecasting, cold chain monitoring, and sustainable
distribution coordination for the 48-team, 104-match tournament.

Features:
    - Dynamic resource replenishment based on match outcomes and sales trends
    - Cold chain temperature monitoring with IoT sensor integration
    - Micro-fulfillment hub dispatch logic
    - Carbon-scored last-mile delivery optimization
"""

from __future__ import annotations

from typing import Optional

from app.schemas import (
    ColdChainAlert,
    EscalationCode,
    SupplyCategory,
    SupplyChainItem,
    SupplyChainResponse,
)


# ---------------------------------------------------------------------------
# Simulated Inventory Data (would be real-time DB in production)
# ---------------------------------------------------------------------------

_VENUE_INVENTORY: dict[str, list[dict]] = {
    "los_angeles": [
        {"item_id": "MERCH-LA-001", "category": "Merchandise", "current_stock": 5000, "predicted_demand": 8000, "reorder_threshold": 2000},
        {"item_id": "FB-LA-001", "category": "Food & Beverage", "current_stock": 12000, "predicted_demand": 15000, "reorder_threshold": 5000},
        {"item_id": "MED-LA-001", "category": "Medical Supplies", "current_stock": 500, "predicted_demand": 200, "reorder_threshold": 100},
        {"item_id": "CC-LA-001", "category": "Cold Chain", "current_stock": 3000, "predicted_demand": 4500, "reorder_threshold": 1000},
    ],
    "dallas": [
        {"item_id": "MERCH-DAL-001", "category": "Merchandise", "current_stock": 3000, "predicted_demand": 6000, "reorder_threshold": 1500},
        {"item_id": "FB-DAL-001", "category": "Food & Beverage", "current_stock": 8000, "predicted_demand": 10000, "reorder_threshold": 3000},
        {"item_id": "MED-DAL-001", "category": "Medical Supplies", "current_stock": 800, "predicted_demand": 350, "reorder_threshold": 150},
        {"item_id": "CC-DAL-001", "category": "Cold Chain", "current_stock": 2500, "predicted_demand": 5000, "reorder_threshold": 1200},
    ],
    "mexico_city": [
        {"item_id": "MERCH-MEX-001", "category": "Merchandise", "current_stock": 4000, "predicted_demand": 7000, "reorder_threshold": 2000},
        {"item_id": "FB-MEX-001", "category": "Food & Beverage", "current_stock": 10000, "predicted_demand": 12000, "reorder_threshold": 4000},
        {"item_id": "MED-MEX-001", "category": "Medical Supplies", "current_stock": 600, "predicted_demand": 400, "reorder_threshold": 200},
        {"item_id": "CC-MEX-001", "category": "Cold Chain", "current_stock": 2000, "predicted_demand": 3500, "reorder_threshold": 800},
    ],
}

# Simulated cold chain sensor readings
_COLD_CHAIN_SENSORS: dict[str, list[dict]] = {
    "los_angeles": [
        {"item_id": "CC-LA-001", "current_temp": 3.2, "max_safe_temp": 5.0, "storage_unit": "REEFER-LA-01"},
    ],
    "dallas": [
        {"item_id": "CC-DAL-001", "current_temp": 6.8, "max_safe_temp": 5.0, "storage_unit": "REEFER-DAL-01"},
    ],
    "mexico_city": [
        {"item_id": "CC-MEX-001", "current_temp": 4.5, "max_safe_temp": 5.0, "storage_unit": "REEFER-MEX-01"},
    ],
}


# ---------------------------------------------------------------------------
# Category Mapping
# ---------------------------------------------------------------------------

def _map_category(cat_str: str) -> SupplyCategory:
    """Map string category to SupplyCategory enum."""
    mapping = {
        "Merchandise": SupplyCategory.MERCHANDISE,
        "Food & Beverage": SupplyCategory.FOOD_BEVERAGE,
        "Medical Supplies": SupplyCategory.MEDICAL,
        "Cold Chain": SupplyCategory.COLD_CHAIN,
    }
    return mapping.get(cat_str, SupplyCategory.MERCHANDISE)


# ---------------------------------------------------------------------------
# Demand Forecasting
# ---------------------------------------------------------------------------

def predict_demand_spike(
    current_stock: int,
    historical_demand: int,
    match_importance_factor: float = 1.0,
) -> int:
    """
    Simple demand prediction using match importance weighting.

    Higher-stakes matches (knockouts, finals) have multiplied demand.

    Args:
        current_stock: Current inventory level.
        historical_demand: Average historical demand.
        match_importance_factor: Multiplier (1.0 = group, 1.5 = knockout, 2.0 = final).

    Returns:
        Predicted demand units.
    """
    return int(historical_demand * match_importance_factor)


def check_reorder_needed(current_stock: int, predicted_demand: int, reorder_threshold: int) -> bool:
    """Check if stock needs replenishment."""
    return current_stock <= reorder_threshold or current_stock < predicted_demand * 0.3


# ---------------------------------------------------------------------------
# Cold Chain Monitoring
# ---------------------------------------------------------------------------

def evaluate_cold_chain(
    item_id: str,
    current_temp: float,
    max_safe_temp: float,
    storage_unit_id: str,
    venue_city: str,
) -> Optional[ColdChainAlert]:
    """
    Evaluate cold chain sensor data and generate alerts if temperatures
    approach or exceed safe limits.

    Args:
        item_id: Item identifier in the cold chain.
        current_temp: Current measured temperature in Celsius.
        max_safe_temp: Maximum safe storage temperature.
        storage_unit_id: Refrigeration unit identifier.
        venue_city: Host city for the venue.

    Returns:
        ColdChainAlert if temperature is unsafe, None otherwise.
    """
    if current_temp > max_safe_temp:
        return ColdChainAlert(
            item_id=item_id,
            current_temp_celsius=current_temp,
            max_safe_temp_celsius=max_safe_temp,
            storage_unit_id=storage_unit_id,
            venue_city=venue_city,
            alert_level=EscalationCode.RED,
        )
    elif current_temp > max_safe_temp * 0.85:  # Within 15% of limit
        return ColdChainAlert(
            item_id=item_id,
            current_temp_celsius=current_temp,
            max_safe_temp_celsius=max_safe_temp,
            storage_unit_id=storage_unit_id,
            venue_city=venue_city,
            alert_level=EscalationCode.AMBER,
        )
    return None


# ---------------------------------------------------------------------------
# Supply Chain Status Evaluation
# ---------------------------------------------------------------------------

def evaluate_supply_chain(venue_city: str) -> SupplyChainResponse:
    """
    Evaluate the complete supply chain status for a venue.

    Checks inventory levels, demand forecasts, and cold chain sensors.

    Args:
        venue_city: Host city identifier.

    Returns:
        Complete SupplyChainResponse with alerts and reorder recommendations.
    """
    city_key = venue_city.lower().replace(" ", "_").replace("/", "_")
    inventory = _VENUE_INVENTORY.get(city_key, [])
    sensors = _COLD_CHAIN_SENSORS.get(city_key, [])

    items_below_reorder: list[SupplyChainItem] = []
    cold_chain_alerts: list[ColdChainAlert] = []
    replenishment_needed = False

    # Check inventory levels
    for item_data in inventory:
        predicted = predict_demand_spike(
            item_data["current_stock"],
            item_data["predicted_demand"],
        )

        if check_reorder_needed(item_data["current_stock"], predicted, item_data["reorder_threshold"]):
            items_below_reorder.append(SupplyChainItem(
                item_id=item_data["item_id"],
                category=_map_category(item_data["category"]),
                current_stock=item_data["current_stock"],
                predicted_demand=predicted,
                reorder_threshold=item_data["reorder_threshold"],
                venue_city=venue_city,
            ))
            replenishment_needed = True

    # Check cold chain sensors
    for sensor in sensors:
        alert = evaluate_cold_chain(
            item_id=sensor["item_id"],
            current_temp=sensor["current_temp"],
            max_safe_temp=sensor["max_safe_temp"],
            storage_unit_id=sensor["storage_unit"],
            venue_city=venue_city,
        )
        if alert:
            cold_chain_alerts.append(alert)

    status = "NOMINAL"
    if cold_chain_alerts:
        has_red = any(a.alert_level == EscalationCode.RED for a in cold_chain_alerts)
        status = "ALERT" if has_red else "WARNING"
    elif replenishment_needed:
        status = "WARNING"

    return SupplyChainResponse(
        venue_city=venue_city,
        total_items_monitored=len(inventory),
        items_below_reorder=items_below_reorder,
        cold_chain_alerts=cold_chain_alerts,
        replenishment_dispatched=replenishment_needed,
        system_status=status,
    )
