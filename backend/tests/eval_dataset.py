"""
AegisSphere — RAG Evaluation Dataset
=====================================
Golden dataset for evaluating the RAG system performance across core metrics:
    - Faithfulness: Grounds responses in retrieved context
    - Context Recall: Verifies search retrieval completeness
    - Context Precision: Checks context relevance

Used with the Ragas evaluation framework for automated quality assessment.
"""

EVALUATION_DATASET = [
    {
        "user_input": "How should fans with reduced mobility travel to Lumen Field in Seattle?",
        "retrieved_contexts": [
            "Sound Transit routes passengers with reduced mobility to Lumen Field via the Weller Street Bridge "
            "station, providing a level, step-free pathway that avoids the steep grades of Pioneer Square."
        ],
        "reference": (
            "Fans with reduced mobility should travel via the Weller Street Bridge station "
            "to access a level, step-free pathway, avoiding Pioneer Square's steep grades."
        ),
    },
    {
        "user_input": "What are the automated safety thresholds for gate crowd control?",
        "retrieved_contexts": [
            "AegisSphere automatically triggers safety intervention workflows and applies the DIM-ICE framework "
            "when zone density exceeds 4.5 persons/m² and pedestrian flow drops below 25 persons/min."
        ],
        "reference": (
            "Safety interventions are automatically triggered when crowd density "
            "exceeds 4.5 persons/m² and flow rate falls below 25 persons/min."
        ),
    },
    {
        "user_input": "What is the DIM-ICE framework used for in crowd safety?",
        "retrieved_contexts": [
            "The DIM-ICE framework classifies crowd incidents into three categories: Design (architectural flow "
            "constraints), Information (signage and multilingual instruction gaps), and Management (staff routing "
            "and deployment). It evaluates incidents across three movement phases: Ingress, Circulation, and Egress."
        ],
        "reference": (
            "DIM-ICE classifies crowd incidents as Design (spatial), Information (signage), "
            "or Management (staffing) across Ingress, Circulation, and Egress phases."
        ),
    },
    {
        "user_input": "How does the system handle extreme heat at AT&T Stadium in Dallas?",
        "retrieved_contexts": [
            "AT&T Stadium in Dallas faces humid heat waves exceeding 100°F and severe thunderstorms. "
            "The key operational priority is managing high-heat park-and-ride shuttle operations with "
            "climate-controlled accessible shuttles and shaded pathways with hydration stations."
        ],
        "reference": (
            "Dallas operations prioritize high-heat shuttle management with A/C vehicles "
            "and shaded pathways with hydration stations to combat 100°F+ temperatures."
        ),
    },
    {
        "user_input": "What security designation do US venues receive?",
        "retrieved_contexts": [
            "Each of the 78 matches in the United States is designated as a National Special Security Event (NSSE), "
            "bringing security operations under unified federal direction. The US venues utilize a $625 million "
            "safety grant package from the Federal Emergency Management Agency (FEMA)."
        ],
        "reference": (
            "All US matches receive National Special Security Event (NSSE) designation "
            "with $625M in FEMA safety grants under unified federal security direction."
        ),
    },
    {
        "user_input": "What are the FAA drone restrictions around World Cup venues?",
        "retrieved_contexts": [
            "All US World Cup venues have FAA Temporary Flight Restrictions (TFR) establishing No Drone Zones "
            "within 5.6 kilometers (3 nautical miles) of each stadium during match-day windows. "
            "Violations carry criminal prosecution under 18 U.S.C. § 32 and civil fines up to $250,000."
        ],
        "reference": (
            "FAA TFRs prohibit UAS/drone operations within 5.6km of US venues on match days. "
            "Violations face criminal prosecution and fines up to $250,000."
        ),
    },
    {
        "user_input": "How does AegisSphere handle cold chain logistics?",
        "retrieved_contexts": [
            "The system integrates with IoT temperature sensors inside delivery vehicles and on-site storage units. "
            "When storage temperatures approach unsafe limits, the orchestrator detects the breach and "
            "automatically issues routing adjustments to protect perishable food, beverages, and medical supplies."
        ],
        "reference": (
            "IoT temperature sensors monitor cold chain items in transit and storage. "
            "Automated routing adjustments protect perishables when temps approach unsafe limits."
        ),
    },
    {
        "user_input": "What WCAG accessibility standards does the frontend meet?",
        "retrieved_contexts": [
            "AegisSphere achieves WCAG 2.1 Level AA compliance including: 4.5:1 minimum contrast ratio (1.4.3), "
            "200% text resize without loss of functionality (1.4.4), full keyboard operability (2.1.1), "
            "visible focus indicators (2.4.7), and programmatic language declaration for translated content (3.1.2)."
        ],
        "reference": (
            "WCAG 2.1 AA compliance: 4.5:1 contrast (1.4.3), 200% text resize (1.4.4), "
            "keyboard navigation (2.1.1), visible focus (2.4.7), language declaration (3.1.2)."
        ),
    },
    {
        "user_input": "How many matches are allocated to MetLife Stadium?",
        "retrieved_contexts": [
            "MetLife Stadium in New York/NJ hosts Round of 16 matches and the FIFA World Cup 2026 Final Match. "
            "The venue faces complex multi-state rail transfers and receives $66.2M in federal security funding "
            "under NSSE designation."
        ],
        "reference": (
            "MetLife Stadium hosts Round of 16 and the Final Match, with $66.2M in "
            "federal funding and cross-jurisdictional transit coordination as the key priority."
        ),
    },
    {
        "user_input": "How does the system protect against prompt injection attacks?",
        "retrieved_contexts": [
            "AegisSphere implements defense-in-depth: input filters screen for intent overrides, adversarial "
            "formatting, and suspicious instruction sequences. A dual-LLM architecture isolates data analysis "
            "(Quarantined Executor) from system orchestration (Privileged Planner). Schema-enforced tool "
            "validation and output policy verification prevent unauthorized actions and information leakage."
        ],
        "reference": (
            "Defense-in-depth pipeline: input sanitization, dual-LLM capability mediation "
            "(P-LLM planner + Q-LLM executor), schema-enforced tools, and output verification."
        ),
    },
]
