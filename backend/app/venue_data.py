"""
AegisSphere — Host City Venue Data Models
==========================================
Complete operational profiles for all 16 FIFA World Cup 2026 host cities.
Each profile captures transit vulnerabilities, climate risks, security
designations, and key operational priorities as specified in the
metropolitan vulnerability analysis.
"""

from __future__ import annotations

from app.schemas import VenueProfile, SecurityDesignation


# ---------------------------------------------------------------------------
# All 16 Host City Venue Profiles
# ---------------------------------------------------------------------------

VENUE_PROFILES: dict[str, VenueProfile] = {
    "los_angeles": VenueProfile(
        city="Los Angeles",
        venue_name="SoFi Stadium",
        country="United States",
        matches_allocated="8 Matches",
        transit_vulnerabilities="Heavy car dependency, extreme LAX airport congestion",
        climate_risks="Extreme heat, coastal wildfire smoke",
        security_designation=SecurityDesignation.NSSE,
        security_funding="Peak federal funding share",
        key_operational_priority="Intercepting airport-to-stadium rideshare bottlenecks",
        latitude=33.9535,
        longitude=-118.3392,
    ),
    "dallas": VenueProfile(
        city="Dallas",
        venue_name="AT&T Stadium",
        country="United States",
        matches_allocated="Round of 32 & 16",
        transit_vulnerabilities="Highly limited public transit infrastructure",
        climate_risks="Humid heat waves (exceeding 100°F), severe thunderstorms",
        security_designation=SecurityDesignation.NSSE,
        security_funding="$51.6M federal funding share",
        key_operational_priority="Managing high-heat park-and-ride shuttle operations",
        latitude=32.7473,
        longitude=-97.0945,
    ),
    "houston": VenueProfile(
        city="Houston",
        venue_name="NRG Stadium",
        country="United States",
        matches_allocated="Round of 16",
        transit_vulnerabilities="Car-dependent metro layout",
        climate_risks="Severe heat index, gulf hurricane threats",
        security_designation=SecurityDesignation.NSSE,
        security_funding="Federal security funding",
        key_operational_priority="Climate-adaptive HVAC grid stabilization",
        latitude=29.6847,
        longitude=-95.4107,
    ),
    "miami": VenueProfile(
        city="Miami",
        venue_name="Hard Rock Stadium",
        country="United States",
        matches_allocated="Round of 32",
        transit_vulnerabilities="Extreme airport surge, lack of light rail",
        climate_risks="Tropical storms, coastal flooding, heat index illness",
        security_designation=SecurityDesignation.NSSE,
        security_funding="Federal security funding",
        key_operational_priority="Evacuation routing under flash flood warnings",
        latitude=25.9580,
        longitude=-80.2389,
    ),
    "seattle": VenueProfile(
        city="Seattle",
        venue_name="Lumen Field",
        country="United States",
        matches_allocated="6 Matches",
        transit_vulnerabilities="Concourse pinch points, localized rail delays",
        climate_risks="Sudden summer downpours",
        security_designation=SecurityDesignation.NSSE,
        security_funding="Federal security funding",
        key_operational_priority="Level step-free routing for reduced-mobility fans",
        latitude=47.5952,
        longitude=-122.3316,
    ),
    "new_york_nj": VenueProfile(
        city="New York/NJ",
        venue_name="MetLife Stadium",
        country="United States",
        matches_allocated="Round of 16, Final Match",
        transit_vulnerabilities="Complex multi-state rail transfers",
        climate_risks="Intense summer heat waves",
        security_designation=SecurityDesignation.NSSE,
        security_funding="$66.2M federal funding share",
        key_operational_priority="Cross-jurisdictional transit capacity scaling",
        latitude=40.8128,
        longitude=-74.0742,
    ),
    "atlanta": VenueProfile(
        city="Atlanta",
        venue_name="Mercedes-Benz Stadium",
        country="United States",
        matches_allocated="8 Matches",
        transit_vulnerabilities="Heavy central hub rail congestion",
        climate_risks="High humidity index, severe thunderstorms",
        security_designation=SecurityDesignation.NSSE,
        security_funding="$73.4M federal funding share",
        key_operational_priority="Mass transit gate capacity distribution",
        latitude=33.7553,
        longitude=-84.4006,
    ),
    "boston": VenueProfile(
        city="Boston",
        venue_name="Gillette Stadium",
        country="United States",
        matches_allocated="Quarter-finals",
        transit_vulnerabilities="Single-track commuter rail limitations",
        climate_risks="Coastal storms",
        security_designation=SecurityDesignation.NSSE,
        security_funding="Federal security funding",
        key_operational_priority="Post-match commuter train embarkation scheduling",
        latitude=42.0909,
        longitude=-71.2643,
    ),
    "philadelphia": VenueProfile(
        city="Philadelphia",
        venue_name="Lincoln Financial Field",
        country="United States",
        matches_allocated="6 Matches",
        transit_vulnerabilities="Stadium complex subway bottleneck at AT&T Station",
        climate_risks="Summer heat waves, occasional severe thunderstorms",
        security_designation=SecurityDesignation.NSSE,
        security_funding="Federal security funding",
        key_operational_priority="Subway platform crowd management post-match",
        latitude=39.9008,
        longitude=-75.1675,
    ),
    "kansas_city": VenueProfile(
        city="Kansas City",
        venue_name="Arrowhead Stadium",
        country="United States",
        matches_allocated="6 Matches",
        transit_vulnerabilities="Minimal public transit to stadium complex",
        climate_risks="Severe thunderstorms, tornado-season proximity, extreme humidity",
        security_designation=SecurityDesignation.NSSE,
        security_funding="Federal security funding",
        key_operational_priority="Severe weather shelter-in-place coordination",
        latitude=39.0489,
        longitude=-94.4839,
    ),
    "san_francisco": VenueProfile(
        city="San Francisco Bay Area",
        venue_name="Levi's Stadium",
        country="United States",
        matches_allocated="6 Matches",
        transit_vulnerabilities="VTA light rail single-line dependency, highway congestion",
        climate_risks="Extreme heat in South Bay, wildfire smoke events",
        security_designation=SecurityDesignation.NSSE,
        security_funding="Federal security funding",
        key_operational_priority="Light rail surge capacity during post-match egress",
        latitude=37.4033,
        longitude=-121.9694,
    ),
    "vancouver": VenueProfile(
        city="Vancouver",
        venue_name="BC Place",
        country="Canada",
        matches_allocated="7 Matches",
        transit_vulnerabilities="Localized light rail platform constraints",
        climate_risks="Wildfire smoke air quality degradation",
        security_designation=SecurityDesignation.CANADIAN_FEDERAL,
        security_funding="$125M dedicated Canadian security funding",
        key_operational_priority="Coordinating automated transit updates with late matches",
        latitude=49.2768,
        longitude=-123.1118,
    ),
    "toronto": VenueProfile(
        city="Toronto",
        venue_name="BMO Field",
        country="Canada",
        matches_allocated="6 Matches",
        transit_vulnerabilities="Lakeside streetcar congestion",
        climate_risks="Severe humidity",
        security_designation=SecurityDesignation.CANADIAN_FEDERAL,
        security_funding="$90M dedicated Canadian security funding",
        key_operational_priority="Pedestrian diversion around transit access points",
        latitude=43.6332,
        longitude=-79.4186,
    ),
    "mexico_city": VenueProfile(
        city="Mexico City",
        venue_name="Estadio Azteca",
        country="Mexico",
        matches_allocated="5 Matches, Opening Game",
        transit_vulnerabilities="High-altitude urban transport bottlenecks",
        climate_risks="High-altitude air thinning, summer rain",
        security_designation=SecurityDesignation.MEXICAN_FEDERAL,
        security_funding="Federal Mexican Security Directives",
        key_operational_priority="Managing high-altitude heat stress and fan zones",
        latitude=19.3029,
        longitude=-99.1505,
    ),
    "guadalajara": VenueProfile(
        city="Guadalajara",
        venue_name="Estadio Akron",
        country="Mexico",
        matches_allocated="5 Matches",
        transit_vulnerabilities="Limited metro coverage to stadium area",
        climate_risks="Summer rainstorms, moderate altitude effects",
        security_designation=SecurityDesignation.MEXICAN_FEDERAL,
        security_funding="Federal Mexican Security Directives",
        key_operational_priority="Fan zone logistics in tropical rain conditions",
        latitude=20.6810,
        longitude=-103.4626,
    ),
    "monterrey": VenueProfile(
        city="Monterrey",
        venue_name="Estadio BBVA",
        country="Mexico",
        matches_allocated="5 Matches",
        transit_vulnerabilities="Highway-dependent access, limited metro reach",
        climate_risks="Extreme desert heat, flash flooding from sierra runoff",
        security_designation=SecurityDesignation.MEXICAN_FEDERAL,
        security_funding="Federal Mexican Security Directives",
        key_operational_priority="Heat mitigation and hydration station deployment",
        latitude=25.5722,
        longitude=-100.2862,
    ),
}


def get_venue_profile(city_key: str) -> VenueProfile | None:
    """Retrieve a venue profile by its normalized city key."""
    return VENUE_PROFILES.get(city_key.lower().replace(" ", "_").replace("/", "_"))


def get_all_venue_profiles() -> list[VenueProfile]:
    """Return all 16 venue profiles as a list."""
    return list(VENUE_PROFILES.values())


def search_venues_by_country(country: str) -> list[VenueProfile]:
    """Filter venues by country name."""
    return [v for v in VENUE_PROFILES.values() if v.country.lower() == country.lower()]
