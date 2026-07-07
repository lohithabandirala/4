/**
 * AegisSphere — Operations Dashboard Application Logic
 * =====================================================
 * Client-side JavaScript for the AegisSphere operations dashboard.
 * Connects to the FastAPI backend and provides real-time crowd safety
 * monitoring, transit routing, supply chain status, multilingual
 * translation, and security guardrail testing.
 *
 * WCAG 2.1 AA: Full keyboard navigation, ARIA live regions, focus management.
 */

(function () {
    'use strict';

    // -----------------------------------------------------------------------
    // Configuration
    // -----------------------------------------------------------------------

    const API_BASE = 'http://localhost:8000';
    const VENUE_FLAGS = {
        'United States': '🇺🇸',
        'Canada': '🇨🇦',
        'Mexico': '🇲🇽',
    };

    // -----------------------------------------------------------------------
    // DOM References
    // -----------------------------------------------------------------------

    const elements = {
        // Crowd Safety
        zoneSelect: document.getElementById('zone-select'),
        densityInput: document.getElementById('density-input'),
        flowInput: document.getElementById('flow-input'),
        evaluateBtn: document.getElementById('evaluate-btn'),
        densityFill: document.getElementById('density-fill'),
        flowFill: document.getElementById('flow-fill'),
        densityValue: document.getElementById('density-value'),
        flowValue: document.getElementById('flow-value'),
        densityGauge: document.getElementById('density-gauge'),
        flowGauge: document.getElementById('flow-gauge'),
        safetyResult: document.getElementById('safety-analysis-result'),
        crowdSafetyStatus: document.getElementById('crowd-safety-status'),

        // System Status
        systemStatusBadge: document.getElementById('system-status-badge'),
        systemStatusText: document.getElementById('system-status-text'),
        statusDot: document.getElementById('status-dot'),
        alertsValue: document.getElementById('stat-alerts-value'),

        // Venues
        venueList: document.getElementById('venue-list'),

        // Transit
        transitOrigin: document.getElementById('transit-origin'),
        transitVenue: document.getElementById('transit-venue'),
        stepFreeToggle: document.getElementById('step-free-toggle'),
        routeBtn: document.getElementById('route-btn'),
        transitResult: document.getElementById('transit-result'),

        // Supply Chain
        supplyVenue: document.getElementById('supply-venue'),
        supplyBtn: document.getElementById('supply-btn'),
        supplyResult: document.getElementById('supply-result'),

        // Translation
        translateText: document.getElementById('translate-text'),
        sourceLang: document.getElementById('source-lang'),
        targetLang: document.getElementById('target-lang'),
        translateBtn: document.getElementById('translate-btn'),
        translateResult: document.getElementById('translate-result'),

        // Guardrails
        guardrailInput: document.getElementById('guardrail-input'),
        guardrailBtn: document.getElementById('guardrail-btn'),
        guardrailResult: document.getElementById('guardrail-result'),

        // Header
        languageSelect: document.getElementById('language-select'),
        highContrastBtn: document.getElementById('toggle-high-contrast'),
    };

    // -----------------------------------------------------------------------
    // API Client
    // -----------------------------------------------------------------------

    async function apiRequest(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const defaultOptions = {
            headers: { 'Content-Type': 'application/json' },
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                throw new Error('Cannot connect to AegisSphere backend. Is the server running on port 8000?');
            }
            throw error;
        }
    }

    // -----------------------------------------------------------------------
    // Utility Functions
    // -----------------------------------------------------------------------

    function setLoading(element, isLoading) {
        if (isLoading) {
            element.innerHTML = '<div class="loading" role="status" aria-label="Loading">Analyzing...</div>';
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // -----------------------------------------------------------------------
    // Gauge Updates
    // -----------------------------------------------------------------------

    function updateGauges() {
        const density = parseFloat(elements.densityInput.value) || 0;
        const flow = parseFloat(elements.flowInput.value) || 0;

        // Density gauge (0-10 scale)
        const densityPct = Math.min((density / 10) * 100, 100);
        elements.densityFill.style.width = `${densityPct}%`;
        elements.densityValue.innerHTML = `${density.toFixed(1)} <small>p/m²</small>`;
        elements.densityGauge.setAttribute('aria-valuenow', density);

        // Density color
        elements.densityFill.className = 'gauge-fill';
        if (density > 4.5) {
            elements.densityFill.classList.add('gauge-red');
        } else if (density > 3.5) {
            elements.densityFill.classList.add('gauge-amber');
        } else {
            elements.densityFill.classList.add('gauge-green');
        }

        // Flow gauge (0-100 scale)
        const flowPct = Math.min((flow / 100) * 100, 100);
        elements.flowFill.style.width = `${flowPct}%`;
        elements.flowValue.innerHTML = `${flow.toFixed(1)} <small>p/m/min</small>`;
        elements.flowGauge.setAttribute('aria-valuenow', flow);

        // Flow color (inverted — low flow = bad)
        elements.flowFill.className = 'gauge-fill';
        if (flow < 25) {
            elements.flowFill.classList.add('gauge-red');
        } else if (flow < 35) {
            elements.flowFill.classList.add('gauge-amber');
        } else {
            elements.flowFill.classList.add('gauge-green');
        }
    }

    // -----------------------------------------------------------------------
    // Crowd Safety Evaluation
    // -----------------------------------------------------------------------

    async function evaluateSafety() {
        const density = parseFloat(elements.densityInput.value);
        const flow = parseFloat(elements.flowInput.value);
        const zoneId = elements.zoneSelect.value;

        if (isNaN(density) || isNaN(flow)) {
            elements.safetyResult.innerHTML = '<div class="result-card result-warning"><p>Please enter valid density and flow values.</p></div>';
            return;
        }

        setLoading(elements.safetyResult, true);

        try {
            const data = await apiRequest('/v1/ops/evaluate', {
                method: 'POST',
                body: JSON.stringify({ density, flow, zone_id: zoneId }),
            });

            renderSafetyResult(data);
            updateSystemStatus(data.system_status);
        } catch (error) {
            // Fallback: client-side evaluation
            const result = evaluateLocally(density, flow, zoneId);
            renderSafetyResult(result);
            updateSystemStatus(result.system_status);
        }
    }

    function evaluateLocally(density, flow, zoneId) {
        const isCritical = density > 4.5 && flow < 25;
        const isWarning = (density > 3.5 || flow < 35) && !isCritical;

        let status, analysis, action = null;

        if (isCritical) {
            status = 'ALERT';
            analysis = `CRITICAL: Zone '${zoneId}' has exceeded safety thresholds. Density = ${density.toFixed(1)} persons/m² (threshold: 4.5), Flow = ${flow.toFixed(1)} persons/m/min (threshold: 25). Immediate intervention required.`;
            action = {
                action_type: zoneId.includes('concourse') || zoneId.includes('gate') ? 'Design' : 'Management',
                phase: 'Circulation',
                dispatch_staff: true,
                broadcast_message: `🚨 SAFETY NOTICE — Zone ${zoneId}: High density detected. Follow steward directions.`,
                escalation_code: 'RED',
                reroute_zones: ['nearest_available_zone'],
            };
        } else if (isWarning) {
            status = 'WARNING';
            analysis = `WARNING: Zone '${zoneId}' is approaching safety thresholds. Density = ${density.toFixed(1)} persons/m², Flow = ${flow.toFixed(1)} persons/m/min. Heightened monitoring active.`;
        } else {
            status = 'NOMINAL';
            analysis = `NOMINAL: Zone '${zoneId}' is operating within safe parameters. Density = ${density.toFixed(1)} persons/m², Flow = ${flow.toFixed(1)} persons/m/min.`;
        }

        return {
            incident_detected: isCritical,
            safety_analysis: analysis,
            recommended_action: action,
            system_status: status,
        };
    }

    function renderSafetyResult(data) {
        const statusClass = data.system_status === 'ALERT' ? 'result-alert'
            : data.system_status === 'WARNING' ? 'result-warning'
            : 'result-nominal';

        const statusIcon = data.system_status === 'ALERT' ? '🚨'
            : data.system_status === 'WARNING' ? '⚠️'
            : '✅';

        const badgeClass = data.system_status === 'ALERT' ? 'badge-red'
            : data.system_status === 'WARNING' ? 'badge-amber'
            : 'badge-green';

        // Update panel badge
        elements.crowdSafetyStatus.className = `panel-badge ${badgeClass}`;
        elements.crowdSafetyStatus.textContent = data.system_status;

        let html = `
            <div class="result-card ${statusClass}">
                <div class="result-header">
                    <span aria-hidden="true">${statusIcon}</span>
                    <span class="result-status">${data.system_status}</span>
                </div>
                <div class="result-body">
                    <p>${escapeHtml(data.safety_analysis)}</p>
        `;

        if (data.recommended_action) {
            const action = data.recommended_action;
            html += `
                <div class="result-detail">
                    <p><strong>DIM-ICE Classification:</strong> ${escapeHtml(action.action_type)}</p>
                    <p><strong>Phase:</strong> ${escapeHtml(action.phase || 'Circulation')}</p>
                    <p><strong>Escalation:</strong>
                        <span class="result-tag badge-red">${escapeHtml(action.escalation_code)}</span>
                    </p>
                    <p><strong>Staff Dispatch:</strong> ${action.dispatch_staff ? '✅ Required' : '❌ Not Required'}</p>
                    <p><strong>Broadcast:</strong> ${escapeHtml(action.broadcast_message)}</p>
                    ${action.reroute_zones ? `<p><strong>Reroute:</strong> ${action.reroute_zones.map(z => escapeHtml(z)).join(', ')}</p>` : ''}
                </div>
            `;
        }

        html += '</div></div>';
        elements.safetyResult.innerHTML = html;
    }

    function updateSystemStatus(status) {
        const dot = elements.statusDot;
        const badge = elements.systemStatusBadge;

        dot.className = 'status-dot';
        if (status === 'ALERT') {
            dot.classList.add('status-red');
            elements.systemStatusText.textContent = 'SAFETY ALERT ACTIVE';
            badge.style.background = 'var(--red-bg)';
            badge.style.borderColor = 'rgba(239, 68, 68, 0.2)';
            badge.style.color = 'var(--red-text)';
            elements.alertsValue.textContent = '1';
        } else if (status === 'WARNING') {
            dot.classList.add('status-amber');
            elements.systemStatusText.textContent = 'HEIGHTENED MONITORING';
            badge.style.background = 'var(--amber-bg)';
            badge.style.borderColor = 'rgba(245, 158, 11, 0.2)';
            badge.style.color = 'var(--amber-text)';
            elements.alertsValue.textContent = '0';
        } else {
            dot.classList.add('status-green');
            elements.systemStatusText.textContent = 'ALL SYSTEMS NOMINAL';
            badge.style.background = 'var(--green-bg)';
            badge.style.borderColor = 'rgba(34, 197, 94, 0.2)';
            badge.style.color = 'var(--green-text)';
            elements.alertsValue.textContent = '0';
        }
    }

    // -----------------------------------------------------------------------
    // Venue List
    // -----------------------------------------------------------------------

    async function loadVenues() {
        try {
            const venues = await apiRequest('/v1/venues');
            renderVenueList(venues);
        } catch (error) {
            // Fallback to static data
            renderVenueListFallback();
        }
    }

    function renderVenueList(venues) {
        elements.venueList.innerHTML = venues.map(venue => `
            <div class="venue-item" role="listitem" tabindex="0" aria-label="${venue.venue_name}, ${venue.city}">
                <span class="venue-flag" aria-hidden="true">${VENUE_FLAGS[venue.country] || '🏟️'}</span>
                <div class="venue-info">
                    <div class="venue-name">${escapeHtml(venue.venue_name)}</div>
                    <div class="venue-city">${escapeHtml(venue.city)}, ${escapeHtml(venue.country)}</div>
                </div>
                <span class="venue-matches">${escapeHtml(venue.matches_allocated)}</span>
            </div>
        `).join('');
    }

    function renderVenueListFallback() {
        const fallbackVenues = [
            { name: 'SoFi Stadium', city: 'Los Angeles', country: 'United States', matches: '8 Matches' },
            { name: 'AT&T Stadium', city: 'Dallas', country: 'United States', matches: 'R32 & R16' },
            { name: 'NRG Stadium', city: 'Houston', country: 'United States', matches: 'R16' },
            { name: 'Hard Rock Stadium', city: 'Miami', country: 'United States', matches: 'R32' },
            { name: 'Lumen Field', city: 'Seattle', country: 'United States', matches: '6 Matches' },
            { name: 'MetLife Stadium', city: 'New York/NJ', country: 'United States', matches: 'R16 + Final' },
            { name: 'Mercedes-Benz Stadium', city: 'Atlanta', country: 'United States', matches: '8 Matches' },
            { name: 'Gillette Stadium', city: 'Boston', country: 'United States', matches: 'QF' },
            { name: 'Lincoln Financial Field', city: 'Philadelphia', country: 'United States', matches: '6 Matches' },
            { name: 'Arrowhead Stadium', city: 'Kansas City', country: 'United States', matches: '6 Matches' },
            { name: "Levi's Stadium", city: 'SF Bay Area', country: 'United States', matches: '6 Matches' },
            { name: 'BC Place', city: 'Vancouver', country: 'Canada', matches: '7 Matches' },
            { name: 'BMO Field', city: 'Toronto', country: 'Canada', matches: '6 Matches' },
            { name: 'Estadio Azteca', city: 'Mexico City', country: 'Mexico', matches: '5 + Opening' },
            { name: 'Estadio Akron', city: 'Guadalajara', country: 'Mexico', matches: '5 Matches' },
            { name: 'Estadio BBVA', city: 'Monterrey', country: 'Mexico', matches: '5 Matches' },
        ];

        elements.venueList.innerHTML = fallbackVenues.map(v => `
            <div class="venue-item" role="listitem" tabindex="0" aria-label="${v.name}, ${v.city}">
                <span class="venue-flag" aria-hidden="true">${VENUE_FLAGS[v.country] || '🏟️'}</span>
                <div class="venue-info">
                    <div class="venue-name">${escapeHtml(v.name)}</div>
                    <div class="venue-city">${escapeHtml(v.city)}, ${escapeHtml(v.country)}</div>
                </div>
                <span class="venue-matches">${escapeHtml(v.matches)}</span>
            </div>
        `).join('');
    }

    // -----------------------------------------------------------------------
    // Transit Routing
    // -----------------------------------------------------------------------

    async function findRoute() {
        const origin = elements.transitOrigin.value;
        const venueCity = elements.transitVenue.value;
        const destination = elements.transitVenue.options[elements.transitVenue.selectedIndex].text;
        const stepFree = elements.stepFreeToggle.checked;

        setLoading(elements.transitResult, true);

        try {
            const data = await apiRequest('/v1/ops/transit', {
                method: 'POST',
                body: JSON.stringify({
                    origin,
                    destination,
                    venue_city: venueCity,
                    require_step_free: stepFree,
                    language: 'en',
                }),
            });
            renderTransitResult(data);
        } catch (error) {
            elements.transitResult.innerHTML = `
                <div class="result-card result-warning">
                    <p>⚠️ Could not connect to routing service. Please ensure the backend is running.</p>
                    <p class="result-body">${escapeHtml(error.message)}</p>
                </div>
            `;
        }
    }

    function renderTransitResult(data) {
        const modeIcons = {
            'Rail': '🚆', 'Light Rail': '🚈', 'Bus': '🚌', 'Shuttle': '🚐',
            'Walking': '🚶', 'Rideshare': '🚗', 'Streetcar': '🚊', 'Accessible Shuttle': '♿',
        };

        let html = `<div class="result-card ${data.is_fully_accessible ? 'result-nominal' : 'result-warning'}">`;

        html += `
            <div class="result-header">
                <span aria-hidden="true">${data.is_fully_accessible ? '♿ ✅' : '🚶'}</span>
                <span class="result-status">${data.is_fully_accessible ? 'FULLY ACCESSIBLE' : 'STANDARD ROUTE'}</span>
            </div>
            <div class="result-body">
                <p><strong>Total Duration:</strong> ${data.total_duration_minutes} minutes</p>
            </div>
        `;

        // Route steps
        html += '<div class="route-steps">';
        data.steps.forEach((step, idx) => {
            html += `
                <div class="route-step">
                    <div class="step-icon">${modeIcons[step.mode] || '📍'}</div>
                    <div class="step-content">
                        <div class="step-mode">${escapeHtml(step.mode)} ${step.is_step_free ? '<span class="step-accessible">♿ Step-free</span>' : ''}</div>
                        <div class="step-instruction">${escapeHtml(step.instruction)}</div>
                        <div class="step-duration">${step.duration_minutes} min</div>
                        ${step.accessibility_notes ? `<div class="step-accessible" style="font-size: var(--text-xs); margin-top: 2px;">ℹ️ ${escapeHtml(step.accessibility_notes)}</div>` : ''}
                    </div>
                </div>
            `;
        });
        html += '</div>';

        // Carbon score
        html += `
            <div class="carbon-score">
                <span>🌱 Green Transport Score:</span>
                <span class="carbon-score-value">${data.carbon_score}/100</span>
            </div>
        `;

        // Warnings
        if (data.warnings && data.warnings.length > 0) {
            html += '<div class="route-warnings">';
            data.warnings.forEach(w => {
                html += `<div class="route-warning">${escapeHtml(w)}</div>`;
            });
            html += '</div>';
        }

        html += '</div>';
        elements.transitResult.innerHTML = html;
    }

    // -----------------------------------------------------------------------
    // Supply Chain
    // -----------------------------------------------------------------------

    async function checkSupply() {
        const venueCity = elements.supplyVenue.value;
        setLoading(elements.supplyResult, true);

        try {
            const data = await apiRequest(`/v1/ops/supply?venue_city=${venueCity}`, {
                method: 'POST',
            });
            renderSupplyResult(data);
        } catch (error) {
            elements.supplyResult.innerHTML = `
                <div class="result-card result-warning">
                    <p>⚠️ Could not connect to supply chain service.</p>
                    <p class="result-body">${escapeHtml(error.message)}</p>
                </div>
            `;
        }
    }

    function renderSupplyResult(data) {
        const statusClass = data.system_status === 'ALERT' ? 'result-alert'
            : data.system_status === 'WARNING' ? 'result-warning'
            : 'result-nominal';

        const statusIcon = data.system_status === 'ALERT' ? '🚨'
            : data.system_status === 'WARNING' ? '⚠️' : '✅';

        let html = `
            <div class="result-card ${statusClass}">
                <div class="result-header">
                    <span aria-hidden="true">${statusIcon}</span>
                    <span class="result-status">${data.system_status}</span>
                </div>
                <div class="result-body">
                    <p><strong>Venue:</strong> ${escapeHtml(data.venue_city)}</p>
                    <p><strong>Items Monitored:</strong> ${data.total_items_monitored}</p>
                    <p><strong>Replenishment Needed:</strong> ${data.replenishment_dispatched ? '✅ Yes' : '❌ No'}</p>
        `;

        if (data.items_below_reorder.length > 0) {
            html += '<div class="result-detail"><p><strong>Items Below Reorder Level:</strong></p><ul>';
            data.items_below_reorder.forEach(item => {
                html += `<li>${escapeHtml(item.item_id)} (${escapeHtml(item.category)}) — Stock: ${item.current_stock}, Demand: ${item.predicted_demand}</li>`;
            });
            html += '</ul></div>';
        }

        if (data.cold_chain_alerts.length > 0) {
            html += '<div class="result-detail"><p><strong>🌡️ Cold Chain Alerts:</strong></p><ul>';
            data.cold_chain_alerts.forEach(alert => {
                html += `<li>${escapeHtml(alert.item_id)} — Temp: ${alert.current_temp_celsius}°C (Max: ${alert.max_safe_temp_celsius}°C) — <span class="result-tag ${alert.alert_level === 'RED' ? 'badge-red' : 'badge-amber'}">${alert.alert_level}</span></li>`;
            });
            html += '</ul></div>';
        }

        html += '</div></div>';
        elements.supplyResult.innerHTML = html;
    }

    // -----------------------------------------------------------------------
    // Translation
    // -----------------------------------------------------------------------

    async function translateText() {
        const text = elements.translateText.value;
        const sourceLang = elements.sourceLang.value;
        const targetLang = elements.targetLang.value;

        if (!text.trim()) return;
        setLoading(elements.translateResult, true);

        try {
            const data = await apiRequest('/v1/ops/translate', {
                method: 'POST',
                body: JSON.stringify({
                    text,
                    source_language: sourceLang,
                    target_language: targetLang,
                    context: 'stadium_operations',
                }),
            });
            renderTranslationResult(data);
        } catch (error) {
            elements.translateResult.innerHTML = `
                <div class="result-card result-warning">
                    <p>⚠️ Could not connect to translation service.</p>
                </div>
            `;
        }
    }

    function renderTranslationResult(data) {
        elements.translateResult.innerHTML = `
            <div class="result-card result-nominal">
                <div class="translated-text" lang="${escapeHtml(data.html_lang_attribute)}">${escapeHtml(data.translated_text)}</div>
                <div class="translation-meta">
                    lang="${escapeHtml(data.html_lang_attribute)}" • ${escapeHtml(data.source_language)} → ${escapeHtml(data.target_language)}
                </div>
            </div>
        `;
    }

    // -----------------------------------------------------------------------
    // Security Guardrail Testing
    // -----------------------------------------------------------------------

    async function testGuardrail() {
        const query = elements.guardrailInput.value;
        if (!query.trim()) return;

        setLoading(elements.guardrailResult, true);

        try {
            const response = await fetch(`${API_BASE}/v1/ops/query?query=${encodeURIComponent(query)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            });

            if (response.status === 403) {
                const data = await response.json();
                renderGuardrailResult(false, data.detail);
            } else if (response.ok) {
                const data = await response.json();
                renderGuardrailResult(true, data.response, data.domain_relevant);
            } else {
                renderGuardrailResult(false, 'Unexpected error');
            }
        } catch (error) {
            // Client-side guardrail test fallback
            const injectionPatterns = [
                /ignore\s+(all\s+)?previous\s+(instructions?|prompts?|rules?)/i,
                /reveal\s+(your\s+)?(system\s+)?prompt/i,
                /override\s+safety\s+protocols?/i,
                /pretend\s+to\s+be/i,
                /disable\s+(guardrails?|safety|security)/i,
            ];

            const isInjection = injectionPatterns.some(p => p.test(query));
            if (isInjection) {
                renderGuardrailResult(false, 'Prompt injection detected — query blocked by security filter');
            } else {
                renderGuardrailResult(true, 'Input passed all security checks', true);
            }
        }
    }

    function renderGuardrailResult(isSafe, message, domainRelevant = true) {
        const resultClass = isSafe ? 'result-safe' : 'result-blocked';
        const icon = isSafe ? '✅' : '🚫';
        const status = isSafe ? 'PASSED' : 'BLOCKED';

        elements.guardrailResult.innerHTML = `
            <div class="result-card ${resultClass}">
                <div class="result-header">
                    <span aria-hidden="true">${icon}</span>
                    <span class="result-status">${status}</span>
                </div>
                <div class="result-body">
                    <p>${escapeHtml(message)}</p>
                    ${!domainRelevant && isSafe ? '<p><em>Note: Query is outside AegisSphere\'s operational domain.</em></p>' : ''}
                </div>
            </div>
        `;
    }

    // -----------------------------------------------------------------------
    // High Contrast Toggle
    // -----------------------------------------------------------------------

    function toggleHighContrast() {
        document.body.classList.toggle('high-contrast');
        const isHighContrast = document.body.classList.contains('high-contrast');
        elements.highContrastBtn.setAttribute('aria-pressed', isHighContrast);
        localStorage.setItem('aegis-high-contrast', isHighContrast);
    }

    // -----------------------------------------------------------------------
    // Preset Buttons
    // -----------------------------------------------------------------------

    function setupPresets() {
        document.querySelectorAll('.btn-preset').forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.getAttribute('data-query');
                elements.guardrailInput.value = query;
                elements.guardrailInput.focus();
            });
        });
    }

    // -----------------------------------------------------------------------
    // Event Listeners
    // -----------------------------------------------------------------------

    function init() {
        // Gauges update on input change
        elements.densityInput.addEventListener('input', updateGauges);
        elements.flowInput.addEventListener('input', updateGauges);

        // Button clicks
        elements.evaluateBtn.addEventListener('click', evaluateSafety);
        elements.routeBtn.addEventListener('click', findRoute);
        elements.supplyBtn.addEventListener('click', checkSupply);
        elements.translateBtn.addEventListener('click', translateText);
        elements.guardrailBtn.addEventListener('click', testGuardrail);
        elements.highContrastBtn.addEventListener('click', toggleHighContrast);

        // Keyboard: Enter key on inputs
        elements.densityInput.addEventListener('keydown', e => { if (e.key === 'Enter') evaluateSafety(); });
        elements.flowInput.addEventListener('keydown', e => { if (e.key === 'Enter') evaluateSafety(); });
        elements.guardrailInput.addEventListener('keydown', e => { if (e.key === 'Enter') testGuardrail(); });

        // Preset buttons
        setupPresets();

        // Restore high contrast preference
        if (localStorage.getItem('aegis-high-contrast') === 'true') {
            document.body.classList.add('high-contrast');
            elements.highContrastBtn.setAttribute('aria-pressed', 'true');
        }

        // Initial gauge render
        updateGauges();

        // Load venue data
        loadVenues();
    }

    // -----------------------------------------------------------------------
    // Start Application
    // -----------------------------------------------------------------------

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
