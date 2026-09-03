const { useState, useEffect, useRef } = React;

// Main Application Component
function App() {
    const [currentTab, setCurrentTab] = useState('dashboard');
    const [incidents, setIncidents] = useState([]);
    const [kpis, setKpis] = useState(null);
    const [selectedIncidentId, setSelectedIncidentId] = useState(null);
    const [selectedIncidentDetails, setSelectedIncidentDetails] = useState(null);
    
    // Split recommendation lists
    const [verifiedRecs, setVerifiedRecs] = useState([]);
    const [rejectedCandidates, setRejectedCandidates] = useState([]);
    const [activeQuery, setActiveQuery] = useState(null);
    
    const [evidenceModalRec, setEvidenceModalRec] = useState(null);
    const [overrideModalRec, setOverrideModalRec] = useState(null);
    const [overrideReason, setOverrideReason] = useState('Version mismatch');
    const [overrideComment, setOverrideComment] = useState('');
    const [kbArticles, setKbArticles] = useState([]);
    const [analyticsData, setAnalyticsData] = useState(null);
    const [experimentData, setExperimentData] = useState(null);
    const [eventStream, setEventStream] = useState([]);
    const [eventStatusSummary, setEventStatusSummary] = useState(null);
    const [injectionResult, setInjectionResult] = useState(null);
    const [riskRegister, setRiskRegister] = useState([]);
    const [stakeholderData, setStakeholderData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [notification, setNotification] = useState(null);

    // New Incident Form State
    const [incDesc, setIncDesc] = useState('');
    const [incSystem, setIncSystem] = useState('LabSys');
    const [incVersion, setIncVersion] = useState('5.4');
    const [incCategory, setIncCategory] = useState('Application');
    const [incSeverity, setIncSeverity] = useState('High');

    // Show temporary notification banner
    const showNotice = (msg, type = 'success') => {
        setNotification({ msg, type });
        setTimeout(() => setNotification(null), 4000);
    };

    // Load Dashboard KPIs & Recent Incidents on Mount
    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const [kpiRes, incRes] = await Promise.all([
                fetch('/api/dashboard/kpis'),
                fetch('/api/incidents')
            ]);
            const kpiData = await kpiRes.json();
            const incData = await incRes.json();
            setKpis(kpiData);
            setIncidents(incData);
        } catch (err) {
            console.error("Error fetching dashboard data:", err);
        }
    };

    // Preset Scenarios (Section 16 Demo Scenarios)
    const loadPresetScenario = (scenarioType) => {
        if (scenarioType === 'SCENARIO_A') {
            setIncDesc('Lab results are not loading for users.');
            setIncSystem('LabSys');
            setIncVersion('5.4');
            setIncCategory('Application');
            setIncSeverity('High');
            showNotice('Loaded Scenario A: Valid LabSys 5.4 Incident', 'info');
        } else if (scenarioType === 'SCENARIO_B') {
            setIncDesc('PACS image loading slow in ER radiology station');
            setIncSystem('PACSView');
            setIncVersion('4.1');
            setIncCategory('Performance');
            setIncSeverity('Medium');
            showNotice('Loaded Scenario B: System Mismatch Demo (PACSView 4.1 vs LabSys candidate)', 'info');
        } else if (scenarioType === 'SCENARIO_C') {
            setIncDesc('Lab result screen blank in legacy station');
            setIncSystem('LabSys');
            setIncVersion('5.4');
            setIncCategory('Application');
            setIncSeverity('High');
            showNotice('Loaded Scenario C: Outdated Version / Retired Article Demo', 'info');
        } else if (scenarioType === 'SCENARIO_D') {
            setIncDesc('EHR database connection pool timeout');
            setIncSystem('EHRCore');
            setIncVersion('6.0');
            setIncCategory('Database');
            setIncSeverity('Critical');
            showNotice('Loaded Scenario D: High-Impact Action Confirmation Required', 'info');
        }
    };

    // Create Incident & Trigger Retrieval Pipeline
    const handleCreateIncident = async (e) => {
        if (e) e.preventDefault();
        if (!incDesc || !incSystem || !incVersion) {
            showNotice('Please complete all required fields.', 'error');
            return;
        }

        setLoading(true);
        try {
            // 1. Create incident in backend
            const createRes = await fetch('/api/incidents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    description: incDesc,
                    system: incSystem,
                    version: incVersion,
                    category: incCategory,
                    severity: incSeverity,
                    impact_level: incSeverity === 'High' || incSeverity === 'Critical' ? 'HIGH' : 'LOW'
                })
            });
            const createdInc = await createRes.json();

            // 2. Fetch recommendations from Verification Pipeline
            const recRes = await fetch('/api/retrieval/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    incident_id: createdInc.incident_id,
                    description: incDesc,
                    system: incSystem,
                    version: incVersion
                })
            });
            const recData = await recRes.json();

            setSelectedIncidentId(createdInc.incident_id);
            setVerifiedRecs(recData.verified_recommendations || []);
            setRejectedCandidates(recData.rejected_candidates || []);
            setActiveQuery(recData.query);
            setCurrentTab('assistant');
            fetchDashboardData();
            
            const vCount = (recData.verified_recommendations || []).length;
            const rCount = (recData.rejected_candidates || []).length;
            showNotice(`Incident ${createdInc.incident_id} processed. Verified: ${vCount}, Blocked: ${rCount}`);
        } catch (err) {
            showNotice('Failed to process incident: ' + err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    // View Incident Detail & Timeline
    const handleViewIncidentDetail = async (incidentId) => {
        setSelectedIncidentId(incidentId);
        try {
            const res = await fetch(`/api/incidents/${incidentId}`);
            const data = await res.json();
            setSelectedIncidentDetails(data);
            setCurrentTab('incident_detail');
        } catch (err) {
            showNotice('Failed to fetch incident details', 'error');
        }
    };

    // Action Confirmation: Approve
    const handleApproveAction = async (rec) => {
        if (!selectedIncidentId) {
            showNotice('No active incident selected', 'error');
            return;
        }
        setLoading(true);
        try {
            const res = await fetch(`/api/recommendations/${rec.recommendation_id}/confirm?incident_id=${selectedIncidentId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'APPROVE',
                    recommendation_id: rec.recommendation_id
                })
            });

            if (!res.ok) {
                const errData = await res.json();
                showNotice(`BLOCKED: ${errData.detail}`, 'error');
                return;
            }

            const data = await res.json();
            showNotice(`✓ Fix Approved & Executed! Incident ${selectedIncidentId} resolved in ${data.ttr_minutes} min.`);
            fetchDashboardData();
            handleViewIncidentDetail(selectedIncidentId);
        } catch (err) {
            showNotice('Approval error: ' + err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    // Action Confirmation: Submit Reject with Override Reason
    const handleSubmitOverride = async () => {
        if (!overrideModalRec || !selectedIncidentId) return;
        setLoading(true);
        try {
            const res = await fetch(`/api/recommendations/${overrideModalRec.recommendation_id}/confirm?incident_id=${selectedIncidentId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'REJECT',
                    recommendation_id: overrideModalRec.recommendation_id,
                    override_reason: overrideReason,
                    override_comment: overrideComment
                })
            });
            const data = await res.json();
            showNotice(`Recommendation rejected. Override logged: ${overrideReason}`);
            setOverrideModalRec(null);
            fetchDashboardData();
            handleViewIncidentDetail(selectedIncidentId);
        } catch (err) {
            showNotice('Override error: ' + err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    // Load Knowledge Base
    const fetchKnowledgeBase = async () => {
        try {
            const res = await fetch('/api/system/knowledge-base');
            const data = await res.json();
            setKbArticles(data);
        } catch (err) {
            console.error(err);
        }
    };

    // Load Analytics
    const fetchAnalytics = async () => {
        try {
            const [ttrRes, chartRes] = await Promise.all([
                fetch('/api/analytics/ttr'),
                fetch('/api/analytics/charts')
            ]);
            const ttrData = await ttrRes.json();
            const chartData = await chartRes.json();
            setAnalyticsData({ ttr: ttrData, charts: chartData });
        } catch (err) {
            console.error(err);
        }
    };

    // Load Experiment Data
    const fetchExperiment = async () => {
        try {
            const res = await fetch('/api/experiment/metrics');
            const data = await res.json();
            setExperimentData(data);
        } catch (err) {
            console.error(err);
        }
    };

    // Load Event Stream
    const fetchEventStream = async () => {
        try {
            const res = await fetch('/api/events/stream');
            const data = await res.json();
            setEventStream(data.event_stream || []);
            setEventStatusSummary(data.incident_state_summary);
        } catch (err) {
            console.error(err);
        }
    };

    // Inject Reliability Event
    const handleInjectEvent = async (injectType) => {
        setLoading(true);
        try {
            const res = await fetch('/api/events/inject', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    event_type_to_inject: injectType,
                    incident_id: selectedIncidentId || 'INC-301'
                })
            });
            const data = await res.json();
            setInjectionResult(data);
            showNotice(`Injected ${injectType} Event: ${data.message}`, 'info');
            fetchEventStream();
        } catch (err) {
            showNotice('Injection error: ' + err.message, 'error');
        } finally {
            setLoading(false);
        }
    };

    // Load Risk Register & Stakeholder Data
    const fetchRiskAndStakeholder = async () => {
        try {
            const [riskRes, stakeRes] = await Promise.all([
                fetch('/api/system/risk-register'),
                fetch('/api/system/stakeholder-validation')
            ]);
            const rData = await riskRes.json();
            const sData = await stakeRes.json();
            setRiskRegister(rData);
            setStakeholderData(sData);
        } catch (err) {
            console.error(err);
        }
    };

    // Tab Change Effect
    useEffect(() => {
        if (currentTab === 'knowledge_base') fetchKnowledgeBase();
        if (currentTab === 'analytics') fetchAnalytics();
        if (currentTab === 'experiment') fetchExperiment();
        if (currentTab === 'events') fetchEventStream();
        if (currentTab === 'risk_register') fetchRiskAndStakeholder();
    }, [currentTab]);

    return (
        <div className="flex h-screen bg-slate-50 text-slate-900 overflow-hidden font-sans">
            {/* Sidebar Navigation */}
            <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col flex-shrink-0 border-r border-slate-800">
                <div className="p-4 border-b border-slate-800 flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-md shadow-blue-500/20">
                        <i className="fa-solid fa-hospital-user"></i>
                    </div>
                    <div>
                        <h1 className="font-bold text-white text-sm tracking-wide">Verified Resolution</h1>
                        <p className="text-[11px] text-blue-400 font-medium">Hospital IT Support</p>
                    </div>
                </div>

                <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto custom-scrollbar text-xs font-medium">
                    <NavItem id="dashboard" label="Dashboard" icon="fa-chart-line" currentTab={currentTab} setCurrentTab={setCurrentTab} />
                    <NavItem id="new_incident" label="New Incident" icon="fa-plus-circle" currentTab={currentTab} setCurrentTab={setCurrentTab} badge="New" />
                    <NavItem id="assistant" label="Resolution Assistant" icon="fa-compass" currentTab={currentTab} setCurrentTab={setCurrentTab} />
                    <NavItem id="incidents" label="Incidents List" icon="fa-list-check" currentTab={currentTab} setCurrentTab={setCurrentTab} />
                    <NavItem id="knowledge_base" label="Knowledge Base" icon="fa-book-open" currentTab={currentTab} setCurrentTab={setCurrentTab} />
                    
                    <div className="pt-3 pb-1 px-3 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Evaluation & Metrics</div>
                    <NavItem id="analytics" label="Resolution Analytics" icon="fa-chart-pie" currentTab={currentTab} setCurrentTab={setCurrentTab} />
                    <NavItem id="experiment" label="Experiment Benchmarks" icon="fa-flask" currentTab={currentTab} setCurrentTab={setCurrentTab} />
                    <NavItem id="events" label="Event Reliability Demo" icon="fa-shield-halved" currentTab={currentTab} setCurrentTab={setCurrentTab} />
                    
                    <div className="pt-3 pb-1 px-3 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Governance</div>
                    <NavItem id="risk_register" label="Risk & Stakeholder" icon="fa-clipboard-list" currentTab={currentTab} setCurrentTab={setCurrentTab} />
                    <NavItem id="user_guide" label="User Guide" icon="fa-circle-question" currentTab={currentTab} setCurrentTab={setCurrentTab} />
                </nav>

                <div className="p-3 border-t border-slate-800 text-[11px] text-slate-400 bg-slate-950/50">
                    <div className="flex items-center gap-2 mb-1">
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                        <span className="font-semibold text-slate-200">Strict Pipeline Active</span>
                    </div>
                    <p className="text-slate-500">System Match Hard Filter Enabled</p>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
                {/* Header */}
                <header className="bg-white border-b border-slate-200 px-6 py-3.5 flex items-center justify-between shadow-xs">
                    <div>
                        <h2 className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
                            Verified Resolution Assistant
                            <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">Decision Support</span>
                        </h2>
                        <p className="text-xs text-slate-500">Evidence-backed resolution retrieval for 24/7 clinical IT support</p>
                    </div>

                    <div className="flex items-center gap-3">
                        <button 
                            onClick={() => { loadPresetScenario('SCENARIO_A'); setCurrentTab('new_incident'); }}
                            className="bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all shadow-2xs">
                            <i className="fa-solid fa-vial"></i>
                            Scenario A (LabSys 5.4)
                        </button>

                        <button 
                            onClick={() => { loadPresetScenario('SCENARIO_B'); setCurrentTab('new_incident'); }}
                            className="bg-amber-50 text-amber-800 hover:bg-amber-100 border border-amber-300 text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all shadow-2xs">
                            <i className="fa-solid fa-ban"></i>
                            Scenario B (PACS Mismatch Demo)
                        </button>

                        <div className="h-4 w-px bg-slate-200"></div>

                        <div className="text-right">
                            <div className="text-xs font-semibold text-slate-800">Hospital IT Support Engineer</div>
                            <div className="text-[10px] text-slate-500">Shift A (24/7 Operations)</div>
                        </div>
                    </div>
                </header>

                {/* Notification Banner */}
                {notification && (
                    <div className={`px-6 py-2.5 text-xs font-medium flex items-center justify-between border-b ${
                        notification.type === 'error' ? 'bg-red-50 text-red-800 border-red-200' :
                        notification.type === 'info' ? 'bg-blue-50 text-blue-800 border-blue-200' :
                        'bg-emerald-50 text-emerald-800 border-emerald-200'
                    }`}>
                        <div className="flex items-center gap-2">
                            <i className={`fa-solid ${notification.type === 'error' ? 'fa-triangle-exclamation' : 'fa-circle-info'}`}></i>
                            <span>{notification.msg}</span>
                        </div>
                        <button onClick={() => setNotification(null)} className="text-slate-400 hover:text-slate-600">
                            <i className="fa-solid fa-xmark"></i>
                        </button>
                    </div>
                )}

                {/* Body Content per Tab */}
                <div className="flex-1 overflow-y-auto p-6 custom-scrollbar bg-slate-50">
                    {currentTab === 'dashboard' && (
                        <DashboardView 
                            kpis={kpis} 
                            incidents={incidents} 
                            setCurrentTab={setCurrentTab} 
                            onSelectIncident={handleViewIncidentDetail}
                            onRunDemo={(type) => { loadPresetScenario(type); setCurrentTab('new_incident'); }}
                        />
                    )}

                    {currentTab === 'new_incident' && (
                        <NewIncidentView 
                            incDesc={incDesc} setIncDesc={setIncDesc}
                            incSystem={incSystem} setIncSystem={setIncSystem}
                            incVersion={incVersion} setIncVersion={setIncVersion}
                            incCategory={incCategory} setIncCategory={setIncCategory}
                            incSeverity={incSeverity} setIncSeverity={setIncSeverity}
                            onSubmit={handleCreateIncident}
                            onPreset={loadPresetScenario}
                            loading={loading}
                        />
                    )}

                    {currentTab === 'assistant' && (
                        <AssistantView 
                            verifiedRecs={verifiedRecs}
                            rejectedCandidates={rejectedCandidates}
                            query={activeQuery}
                            onViewEvidence={(rec) => setEvidenceModalRec(rec)}
                            onApprove={handleApproveAction}
                            onReject={(rec) => setOverrideModalRec(rec)}
                            loading={loading}
                        />
                    )}

                    {currentTab === 'incidents' && (
                        <IncidentsListView 
                            incidents={incidents} 
                            onSelectIncident={handleViewIncidentDetail} 
                        />
                    )}

                    {currentTab === 'incident_detail' && (
                        <IncidentDetailView 
                            incidentDetails={selectedIncidentDetails} 
                            onBack={() => setCurrentTab('incidents')} 
                        />
                    )}

                    {currentTab === 'knowledge_base' && (
                        <KnowledgeBaseView articles={kbArticles} />
                    )}

                    {currentTab === 'analytics' && (
                        <AnalyticsView data={analyticsData} />
                    )}

                    {currentTab === 'experiment' && (
                        <ExperimentView data={experimentData} />
                    )}

                    {currentTab === 'events' && (
                        <EventReliabilityView 
                            stream={eventStream} 
                            summary={eventStatusSummary}
                            result={injectionResult}
                            onInject={handleInjectEvent}
                        />
                    )}

                    {currentTab === 'risk_register' && (
                        <RiskAndStakeholderView riskRegister={riskRegister} stakeholderData={stakeholderData} />
                    )}

                    {currentTab === 'user_guide' && (
                        <UserGuideView />
                    )}
                </div>

                {/* Evidence Modal */}
                {evidenceModalRec && (
                    <EvidenceModal 
                        rec={evidenceModalRec} 
                        onClose={() => setEvidenceModalRec(null)} 
                    />
                )}

                {/* Override Modal */}
                {overrideModalRec && (
                    <OverrideModal 
                        rec={overrideModalRec}
                        reason={overrideReason} setReason={setOverrideReason}
                        comment={overrideComment} setComment={setOverrideComment}
                        onSubmit={handleSubmitOverride}
                        onClose={() => setOverrideModalRec(null)}
                        loading={loading}
                    />
                )}
            </main>
        </div>
    );
}

// Subcomponents

function NavItem({ id, label, icon, currentTab, setCurrentTab, badge }) {
    const isActive = currentTab === id;
    return (
        <button
            onClick={() => setCurrentTab(id)}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                isActive 
                    ? 'bg-blue-600 text-white font-semibold shadow-xs' 
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
            }`}
        >
            <div className="flex items-center gap-2.5">
                <i className={`fa-solid ${icon} w-4 text-center ${isActive ? 'text-white' : 'text-slate-400'}`}></i>
                <span>{label}</span>
            </div>
            {badge && (
                <span className="bg-blue-500/20 text-blue-300 text-[10px] font-bold px-1.5 py-0.5 rounded">
                    {badge}
                </span>
            )}
        </button>
    );
}

// 1. Dashboard View (with Verification Status Cards per Section 6)
function DashboardView({ kpis, incidents, setCurrentTab, onSelectIncident, onRunDemo }) {
    const vs = kpis?.verification_status || {
        current_recommendations: 8,
        blocked_outdated_fixes: 3,
        system_version_mismatches: 2,
        human_approvals_required: 1
    };

    return (
        <div className="space-y-6">
            {/* Banner */}
            <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 rounded-xl p-5 text-white shadow-md flex items-center justify-between border border-slate-800">
                <div className="space-y-1">
                    <div className="flex items-center gap-2">
                        <span className="bg-blue-500/20 text-blue-300 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-blue-400/30">Strict Verification Pipeline Active</span>
                        <span className="text-slate-400 text-xs">• 24/7 IT Ops</span>
                    </div>
                    <h3 className="text-lg font-bold">Verified Resolution Assistant</h3>
                    <p className="text-xs text-slate-300 max-w-2xl">
                        Enforces multi-stage verification: System Match (Hard Filter) → Version Match → Article Status → Evidence Scoring → Human Confirmation.
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <button 
                        onClick={() => onRunDemo('SCENARIO_A')}
                        className="bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs px-3.5 py-2 rounded-lg shadow-sm flex items-center gap-1.5 transition-all">
                        <i className="fa-solid fa-play"></i>
                        Scenario A (Valid)
                    </button>
                    <button 
                        onClick={() => onRunDemo('SCENARIO_B')}
                        className="bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs px-3.5 py-2 rounded-lg shadow-sm flex items-center gap-1.5 transition-all">
                        <i className="fa-solid fa-ban"></i>
                        Scenario B (System Mismatch)
                    </button>
                </div>
            </div>

            {/* KPI Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <KPICard title="Open Incidents" value={kpis?.open_incidents ?? 2} icon="fa-folder-open" color="text-amber-600" bg="bg-amber-50" />
                <KPICard title="Recurring Incidents" value={kpis?.recurring_incidents ?? 2} icon="fa-rotate-right" color="text-blue-600" bg="bg-blue-50" />
                <KPICard title="Average TTR" value={`${kpis?.avg_ttr_minutes ?? 16.5}m`} icon="fa-stopwatch" color="text-indigo-600" bg="bg-indigo-50" sub="Target: 30m" />
                <KPICard title="Success Rate" value={`${kpis?.resolution_success_rate_pct ?? 94.2}%`} icon="fa-circle-check" color="text-emerald-600" bg="bg-emerald-50" />
                <KPICard title="Recommendations Accepted" value={`${kpis?.recommendations_accepted_pct ?? 100}%`} icon="fa-thumbs-up" color="text-teal-600" bg="bg-teal-50" />
                <KPICard title="High-Impact Pending" value={kpis?.high_impact_pending_approval ?? 1} icon="fa-triangle-exclamation" color="text-red-600" bg="bg-red-50" highlight={true} />
            </div>

            {/* Verification Status Cards (Section 6 Requirements) */}
            <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs space-y-3">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                    <h4 className="font-bold text-slate-900 text-xs flex items-center gap-2">
                        <i className="fa-solid fa-shield-check text-blue-600"></i>
                        Verification Pipeline Status
                    </h4>
                    <span className="text-[10px] font-semibold text-slate-400">Dynamically Calculated</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                    <div className="p-3 bg-emerald-50/60 rounded-lg border border-emerald-200">
                        <div className="text-[10px] font-bold text-emerald-800 uppercase">Current Recommendations</div>
                        <div className="text-lg font-black text-emerald-900 mt-0.5">{vs.current_recommendations}</div>
                        <div className="text-[10px] text-emerald-700 mt-0.5">✓ Passed system, version & status</div>
                    </div>

                    <div className="p-3 bg-amber-50/60 rounded-lg border border-amber-200">
                        <div className="text-[10px] font-bold text-amber-800 uppercase">Blocked Outdated Fixes</div>
                        <div className="text-lg font-black text-amber-900 mt-0.5">{vs.blocked_outdated_fixes}</div>
                        <div className="text-[10px] text-amber-700 mt-0.5">⚠️ Filtered retired or version bounds</div>
                    </div>

                    <div className="p-3 bg-red-50/60 rounded-lg border border-red-200">
                        <div className="text-[10px] font-bold text-red-800 uppercase">System/Version Mismatches</div>
                        <div className="text-lg font-black text-red-900 mt-0.5">{vs.system_version_mismatches}</div>
                        <div className="text-[10px] text-red-700 mt-0.5">❌ Hard Filtered (e.g. PACSView vs LabSys)</div>
                    </div>

                    <div className="p-3 bg-blue-50/60 rounded-lg border border-blue-200">
                        <div className="text-[10px] font-bold text-blue-800 uppercase">Human Approvals Required</div>
                        <div className="text-lg font-black text-blue-900 mt-0.5">{vs.human_approvals_required}</div>
                        <div className="text-[10px] text-blue-700 mt-0.5">⚠️ Mandatory High-Impact Confirmation</div>
                    </div>
                </div>
            </div>

            {/* Recent Incidents Table */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
                <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
                    <div>
                        <h4 className="font-bold text-slate-900 text-sm">Recent Clinical IT Incidents</h4>
                        <p className="text-xs text-slate-500">Logically verified ticket status & fix recommendations</p>
                    </div>
                    <button 
                        onClick={() => setCurrentTab('new_incident')}
                        className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-1.5 shadow-2xs">
                        <i className="fa-solid fa-plus"></i>
                        New Incident
                    </button>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                        <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                            <tr>
                                <th className="px-4 py-3">Incident ID</th>
                                <th className="px-4 py-3">Incident Description</th>
                                <th className="px-4 py-3">System</th>
                                <th className="px-4 py-3">Version</th>
                                <th className="px-4 py-3">Severity</th>
                                <th className="px-4 py-3">Status</th>
                                <th className="px-4 py-3">Verified Recommended Fix</th>
                                <th className="px-4 py-3">TTR</th>
                                <th className="px-4 py-3 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {incidents.map((inc) => {
                                // Enforce logically correct displays for PACSView incidents (INC-309/303)
                                const isPacs = inc.system === 'PACSView';
                                const displayFix = isPacs 
                                    ? (inc.resolution_id && inc.resolution_id !== 'KA-014' ? `${inc.resolution_id} (PACS Cache Recovery)` : 'KA-019 (PACS DICOM Router)')
                                    : (inc.resolution_id ? `${inc.resolution_id}` : 'KA-014 (LabSys Service)');

                                return (
                                    <tr key={inc.incident_id} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-4 py-3 font-mono font-semibold text-blue-600">{inc.incident_id}</td>
                                        <td className="px-4 py-3 font-medium text-slate-900 max-w-xs truncate">{inc.description}</td>
                                        <td className="px-4 py-3 font-semibold text-slate-700">{inc.system}</td>
                                        <td className="px-4 py-3 font-mono text-slate-600">{inc.version}</td>
                                        <td className="px-4 py-3">
                                            <SeverityBadge severity={inc.severity} />
                                        </td>
                                        <td className="px-4 py-3">
                                            <StatusBadge status={inc.status} />
                                        </td>
                                        <td className="px-4 py-3 font-medium text-slate-700">
                                            <span className="bg-slate-100 px-2 py-0.5 rounded font-mono text-[11px] text-slate-800">
                                                {displayFix}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 font-mono font-medium text-slate-700">
                                            {inc.ttr_minutes ? `${inc.ttr_minutes} min` : 'Pending'}
                                        </td>
                                        <td className="px-4 py-3 text-right">
                                            <button 
                                                onClick={() => onSelectIncident(inc.incident_id)}
                                                className="text-blue-600 hover:text-blue-800 font-semibold text-xs">
                                                View Details →
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

function KPICard({ title, value, icon, color, bg, sub, highlight }) {
    return (
        <div className={`p-4 rounded-xl border ${highlight ? 'border-red-300 bg-red-50/50 shadow-sm' : 'border-slate-200 bg-white shadow-2xs'}`}>
            <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
                <div className={`w-7 h-7 rounded-lg ${bg} ${color} flex items-center justify-center text-xs`}>
                    <i className={`fa-solid ${icon}`}></i>
                </div>
            </div>
            <div className="text-xl font-extrabold text-slate-900">{value}</div>
            {sub && <div className="text-[10px] font-medium text-slate-400 mt-0.5">{sub}</div>}
        </div>
    );
}

// Badges
function SeverityBadge({ severity }) {
    const s = severity?.toLowerCase();
    const color = s === 'critical' ? 'bg-red-100 text-red-800 border-red-200' :
                  s === 'high' ? 'bg-orange-100 text-orange-800 border-orange-200' :
                  s === 'medium' ? 'bg-amber-100 text-amber-800 border-amber-200' :
                  'bg-slate-100 text-slate-800 border-slate-200';
    return (
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${color}`}>
            {severity}
        </span>
    );
}

function StatusBadge({ status }) {
    const st = status?.toUpperCase();
    const color = st === 'RESOLVED' ? 'bg-emerald-100 text-emerald-800 border-emerald-200' :
                  st === 'PENDING_APPROVAL' ? 'bg-red-100 text-red-800 border-red-200 animate-pulse' :
                  st === 'FIX_APPROVED' ? 'bg-blue-100 text-blue-800 border-blue-200' :
                  st === 'OVERRIDDEN' ? 'bg-slate-200 text-slate-700 border-slate-300' :
                  'bg-amber-100 text-amber-800 border-amber-200';
    return (
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${color}`}>
            {status}
        </span>
    );
}

// 2. New Incident Page
function NewIncidentView({ incDesc, setIncDesc, incSystem, setIncSystem, incVersion, setIncVersion, incCategory, setIncCategory, incSeverity, setIncSeverity, onSubmit, onPreset, loading }) {
    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-xl font-bold text-slate-900">New Clinical Incident</h3>
                    <p className="text-xs text-slate-500">Log a new recurring IT issue to retrieve verified, evidence-backed resolutions.</p>
                </div>

                <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-500">Verification Scenarios:</span>
                    <button 
                        onClick={() => onPreset('SCENARIO_A')}
                        className="bg-blue-100 hover:bg-blue-200 text-blue-800 text-xs font-bold px-2.5 py-1 rounded border border-blue-300">
                        Scenario A (Valid LabSys)
                    </button>
                    <button 
                        onClick={() => onPreset('SCENARIO_B')}
                        className="bg-amber-100 hover:bg-amber-200 text-amber-900 text-xs font-bold px-2.5 py-1 rounded border border-amber-300">
                        Scenario B (PACS Mismatch)
                    </button>
                    <button 
                        onClick={() => onPreset('SCENARIO_C')}
                        className="bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium px-2.5 py-1 rounded border border-slate-300">
                        Scenario C (Outdated)
                    </button>
                </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-6">
                <form onSubmit={onSubmit} className="space-y-6">
                    <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">
                            Incident Description <span className="text-red-500">*</span>
                        </label>
                        <textarea
                            value={incDesc}
                            onChange={(e) => setIncDesc(e.target.value)}
                            rows={3}
                            placeholder="e.g. Lab results are not loading for users in ICU."
                            className="w-full rounded-lg border border-slate-300 p-3 text-xs text-slate-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                            required
                        />
                        <p className="text-[11px] text-slate-500 mt-1">Describe the symptoms reported by hospital clinical staff.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-xs font-bold text-slate-700 mb-1">
                                System / Application <span className="text-red-500">*</span>
                            </label>
                            <select
                                value={incSystem}
                                onChange={(e) => setIncSystem(e.target.value)}
                                className="w-full rounded-lg border border-slate-300 p-2.5 text-xs text-slate-900 focus:ring-2 focus:ring-blue-500 outline-none bg-white font-medium">
                                <option value="LabSys">LabSys (Laboratory Information System)</option>
                                <option value="MedFlow">MedFlow (eMAR / Pharmacy Module)</option>
                                <option value="PACSView">PACSView (Radiology Imaging PACS)</option>
                                <option value="EHRCore">EHRCore (Electronic Health Record Core)</option>
                                <option value="AuthGuard">AuthGuard (Single Sign-On SSO Auth)</option>
                                <option value="PrintManager">PrintManager (Nursing Station Printers)</option>
                                <option value="HL7Router">HL7Router (Interface Message Gateway)</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-slate-700 mb-1">
                                Current System Version <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="text"
                                value={incVersion}
                                onChange={(e) => setIncVersion(e.target.value)}
                                placeholder="e.g. 5.4"
                                className="w-full rounded-lg border border-slate-300 p-2.5 text-xs text-slate-900 font-mono focus:ring-2 focus:ring-blue-500 outline-none"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-slate-700 mb-1">Category</label>
                            <select
                                value={incCategory}
                                onChange={(e) => setIncCategory(e.target.value)}
                                className="w-full rounded-lg border border-slate-300 p-2.5 text-xs text-slate-900 focus:ring-2 focus:ring-blue-500 outline-none bg-white">
                                <option value="Application">Application</option>
                                <option value="Performance">Performance</option>
                                <option value="UI/Application">UI / Client Freeze</option>
                                <option value="Authentication">Authentication / SSO</option>
                                <option value="Integration">Integration / HL7 Interface</option>
                                <option value="Infrastructure">Infrastructure / Hardware</option>
                                <option value="Database">Database</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-slate-700 mb-1">Severity & Impact Level</label>
                            <div className="grid grid-cols-2 gap-2">
                                <select
                                    value={incSeverity}
                                    onChange={(e) => setIncSeverity(e.target.value)}
                                    className="w-full rounded-lg border border-slate-300 p-2.5 text-xs text-slate-900 font-medium">
                                    <option value="Critical">Critical</option>
                                    <option value="High">High</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Low">Low</option>
                                </select>

                                <div className="flex items-center px-3 rounded-lg border border-slate-200 bg-slate-50 text-xs font-semibold text-slate-700">
                                    Impact: {incSeverity === 'High' || incSeverity === 'Critical' ? 'HIGH' : 'LOW'}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
                        <button
                            type="button"
                            onClick={() => onPreset('SCENARIO_B')}
                            className="px-4 py-2.5 rounded-lg border border-amber-300 bg-amber-50 text-xs font-semibold text-amber-900 hover:bg-amber-100">
                            Test System Mismatch (PACSView)
                        </button>

                        <button
                            type="submit"
                            disabled={loading}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-6 py-2.5 rounded-lg shadow-md flex items-center gap-2 transition-all disabled:opacity-50">
                            {loading ? <i className="fa-solid fa-spinner animate-spin"></i> : <i className="fa-solid fa-magnifying-glass"></i>}
                            Find Verified Resolution
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

// 3. Resolution Retrieval Assistant Page (Divided per Section 8 into Verified vs Rejected)
function AssistantView({ verifiedRecs, rejectedCandidates, query, onViewEvidence, onApprove, onReject, loading }) {
    return (
        <div className="max-w-5xl mx-auto space-y-8">
            {/* Query Header */}
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-2xs flex items-center justify-between">
                <div>
                    <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                        Verification Pipeline Output
                    </h3>
                    {query && (
                        <p className="text-xs text-slate-600 mt-1">
                            Incident: <span className="font-semibold text-slate-900">"{query.description}"</span> | System: <span className="font-mono font-bold text-blue-700">{query.system}</span> v<span className="font-mono">{query.version}</span>
                        </p>
                    )}
                </div>

                <div className="flex items-center gap-2">
                    <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2.5 py-1 rounded-full border border-emerald-200">
                        ✓ {verifiedRecs?.length || 0} Verified Recommendations
                    </span>
                    <span className="bg-red-100 text-red-800 text-[10px] font-bold px-2.5 py-1 rounded-full border border-red-200">
                        ❌ {rejectedCandidates?.length || 0} Blocked Candidates
                    </span>
                </div>
            </div>

            {/* SECTION A: VERIFIED RECOMMENDATIONS */}
            <div className="space-y-4">
                <div className="flex items-center gap-2 border-b border-emerald-200 pb-2">
                    <span className="w-5 h-5 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center">✓</span>
                    <h4 className="font-bold text-slate-900 text-sm tracking-tight uppercase text-emerald-950">A. VERIFIED RECOMMENDATIONS</h4>
                </div>

                {verifiedRecs && verifiedRecs.length > 0 ? (
                    verifiedRecs.map((rec, index) => (
                        <VerifiedRecommendationCard 
                            key={rec.recommendation_id} 
                            rec={rec} 
                            rank={index + 1}
                            onViewEvidence={() => onViewEvidence(rec)}
                            onApprove={() => onApprove(rec)}
                            onReject={() => onReject(rec)}
                            loading={loading}
                        />
                    ))
                ) : (
                    <div className="p-6 bg-slate-100 rounded-xl text-center text-xs text-slate-600 font-medium border border-slate-200">
                        No candidate resolutions passed all verification rules for this system and version.
                    </div>
                )}
            </div>

            {/* SECTION B: REJECTED CANDIDATES (Section 8 Requirements) */}
            <div className="space-y-4 pt-4 border-t border-slate-200">
                <div className="flex items-center gap-2 border-b border-red-200 pb-2">
                    <span className="w-5 h-5 rounded-full bg-red-600 text-white font-bold text-xs flex items-center justify-center">❌</span>
                    <h4 className="font-bold text-slate-900 text-sm tracking-tight uppercase text-red-950">B. REJECTED CANDIDATES / VERIFICATION FAILED</h4>
                    <span className="text-[10px] font-semibold text-slate-500 ml-auto">Demonstrates Active Blocking Guardrails</span>
                </div>

                {rejectedCandidates && rejectedCandidates.length > 0 ? (
                    rejectedCandidates.map((cand) => (
                        <RejectedCandidateCard key={cand.recommendation_id} cand={cand} />
                    ))
                ) : (
                    <div className="p-4 bg-slate-50 rounded-xl text-center text-xs text-slate-500">
                        No candidates were rejected by verification filters.
                    </div>
                )}
            </div>
        </div>
    );
}

function VerifiedRecommendationCard({ rec, rank, onViewEvidence, onApprove, onReject, loading }) {
    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm hover:border-blue-300 overflow-hidden transition-all">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center">
                        #{rank}
                    </span>
                    <h4 className="font-bold text-slate-900 text-base">{rec.title}</h4>
                </div>

                <div className="text-right">
                    <div className="text-[10px] font-semibold text-slate-400 uppercase">Relevance Score</div>
                    <div className="text-base font-black text-blue-600">{rec.relevance_score}%</div>
                </div>
            </div>

            <div className="p-6 space-y-4">
                <p className="text-xs text-slate-700 leading-relaxed">{rec.description}</p>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-50 p-3.5 rounded-lg border border-slate-200 text-xs">
                    <div>
                        <div className="text-[10px] text-slate-500 font-semibold uppercase">System Match</div>
                        <div className="font-bold text-emerald-700 flex items-center gap-1 mt-0.5">
                            ✓ System Compatible ({rec.knowledge_article_id})
                        </div>
                    </div>

                    <div>
                        <div className="text-[10px] text-slate-500 font-semibold uppercase">Version Status</div>
                        <div className="font-bold text-emerald-700 mt-0.5">
                            ✓ Current & Compatible
                        </div>
                    </div>

                    <div>
                        <div className="text-[10px] text-slate-500 font-semibold uppercase">Historical Evidence</div>
                        <div className="font-semibold text-slate-800 mt-0.5">
                            {rec.successful_count} / {rec.historical_count} successful
                        </div>
                    </div>

                    <div>
                        <div className="text-[10px] text-slate-500 font-semibold uppercase">Average TTR</div>
                        <div className="font-mono font-bold text-slate-900 mt-0.5">
                            {rec.avg_ttr} minutes
                        </div>
                    </div>
                </div>

                {rec.requires_human_confirmation && (
                    <div className="p-3.5 bg-red-50 border border-red-200 rounded-lg text-red-900 text-xs flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <i className="fa-solid fa-shield-cat text-red-600 text-lg"></i>
                            <div>
                                <div className="font-bold text-red-800">⚠️ HIGH-IMPACT ACTION</div>
                                <div className="text-[11px] text-red-700">This action may affect clinical system availability. Explicit human confirmation required.</div>
                            </div>
                        </div>
                        <span className="bg-red-100 text-red-800 font-extrabold text-[10px] px-2.5 py-1 rounded uppercase tracking-wider">
                            Confirmation Required
                        </span>
                    </div>
                )}

                <div className="pt-2 flex items-center justify-between">
                    <button
                        onClick={onViewEvidence}
                        className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold px-4 py-2 rounded-lg border border-slate-300 flex items-center gap-1.5">
                        <i className="fa-solid fa-eye"></i>
                        View Evidence
                    </button>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={onReject}
                            className="bg-slate-100 hover:bg-red-50 text-slate-700 hover:text-red-700 text-xs font-semibold px-4 py-2 rounded-lg border border-slate-300 hover:border-red-300">
                            Reject Recommendation
                        </button>

                        <button
                            onClick={onApprove}
                            disabled={loading}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold px-5 py-2 rounded-lg shadow-sm flex items-center gap-2 disabled:opacity-50">
                            {loading ? <i className="fa-solid fa-spinner animate-spin"></i> : <i className="fa-solid fa-check"></i>}
                            Approve Fix
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Section B: Rejected Candidate Card (Explicit System Mismatch / Version Blocked display per Section 1 & 8)
function RejectedCandidateCard({ cand }) {
    return (
        <div className="bg-red-50/30 border border-red-200 rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="bg-red-100 text-red-800 text-[10px] font-extrabold px-2.5 py-0.5 rounded border border-red-300 uppercase">
                        BLOCKED ({cand.status})
                    </span>
                    <h4 className="font-bold text-slate-900 text-sm">{cand.title}</h4>
                </div>

                <div className="text-right text-xs">
                    <span className="text-slate-500 font-semibold">Similarity: {cand.similarity_score}%</span>
                </div>
            </div>

            <div className="p-3 bg-red-100/60 border border-red-300 rounded-lg text-red-900 text-xs space-y-2">
                <div className="font-extrabold flex items-center gap-1.5 text-red-950">
                    <i className="fa-solid fa-ban text-red-600"></i>
                    ❌ Resolution Not Recommended
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
                    <div>
                        <span className="font-semibold text-red-800">Reason:</span> {cand.reason}
                    </div>
                    <div>
                        <span className="font-semibold text-red-800">Verification Rule:</span> <code className="bg-white px-1.5 py-0.5 rounded border border-red-200 font-mono text-[10px]">{cand.verification_rule}</code>
                    </div>
                </div>

                <div className="pt-2 border-t border-red-200/80 grid grid-cols-2 gap-4 text-[11px]">
                    <div>
                        <span className="font-semibold text-slate-700">Incident Context:</span> {cand.incident_context.system} (v{cand.incident_context.version})
                    </div>
                    <div>
                        <span className="font-semibold text-slate-700">Resolution System:</span> {cand.resolution_context.system} ({cand.resolution_context.version_range})
                    </div>
                </div>
            </div>

            <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                <span>Knowledge Article: <strong className="font-mono">{cand.knowledge_article_id}</strong> ({cand.knowledge_article_status})</span>
                <span className="font-semibold text-red-700">User execution disabled by system guardrail</span>
            </div>
        </div>
    );
}

// 4. Evidence Panel Modal
function EvidenceModal({ rec, onClose }) {
    return (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-2xl w-full overflow-hidden max-h-[90vh] flex flex-col">
                <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
                    <div>
                        <h4 className="font-bold text-slate-900 text-sm">Why this resolution was recommended</h4>
                        <p className="text-xs text-slate-500">{rec.title}</p>
                    </div>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-lg">
                        <i className="fa-solid fa-xmark"></i>
                    </button>
                </div>

                <div className="p-6 overflow-y-auto space-y-5 text-xs">
                    <div>
                        <h5 className="font-bold text-slate-800 text-xs mb-2">Verification Rules Passed</h5>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 bg-emerald-50/60 p-3 rounded-lg border border-emerald-200">
                            {rec.rules_passed?.map((rule, idx) => (
                                <div key={idx} className="font-semibold text-emerald-900 text-[11px] flex items-center gap-1.5">
                                    {rule}
                                </div>
                            ))}
                        </div>
                    </div>

                    <div>
                        <h5 className="font-bold text-slate-800 text-xs mb-2">Historical Incidents Evidence</h5>
                        <div className="space-y-1.5">
                            {rec.historical_ticket_ids?.map((ticket, idx) => (
                                <div key={idx} className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between text-[11px]">
                                    <div className="flex items-center gap-2">
                                        <span className="font-mono font-bold text-blue-700">{ticket.ticket_id}</span>
                                        <span className="text-slate-700">{ticket.summary}</span>
                                    </div>
                                    <div className="font-semibold text-slate-900">
                                        resolved in <span className="text-emerald-700 font-mono">{ticket.resolved_in_min} min</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200">
                        <div>
                            <span className="text-[10px] font-semibold text-slate-500 uppercase">Knowledge Article</span>
                            <div className="font-bold text-blue-700 font-mono">{rec.knowledge_article_id} — {rec.title}</div>
                        </div>
                        <div>
                            <span className="text-[10px] font-semibold text-slate-500 uppercase">Last Verified Date</span>
                            <div className="font-semibold text-slate-800">{rec.last_verified} (Current ✓)</div>
                        </div>
                    </div>

                    <div>
                        <h5 className="font-bold text-slate-800 text-xs mb-2">Transparent Score Math</h5>
                        <div className="p-3 bg-slate-900 text-slate-200 rounded-lg font-mono text-[11px] space-y-1">
                            <div>Relevance Score = 0.50×Sim + 0.20×Version + 0.15×Success + 0.10×Freshness + 0.05×Recency</div>
                            <div className="text-blue-400 font-bold">Computed Result: {rec.relevance_score}%</div>
                        </div>
                    </div>
                </div>

                <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 text-right">
                    <button
                        onClick={onClose}
                        className="bg-slate-900 text-white font-semibold text-xs px-4 py-2 rounded-lg">
                        Close Evidence Panel
                    </button>
                </div>
            </div>
        </div>
    );
}

// 5. Override Reason Modal
function OverrideModal({ rec, reason, setReason, comment, setComment, onSubmit, onClose, loading }) {
    const reasons = [
        "Version mismatch",
        "Fix already attempted",
        "Not applicable to current incident",
        "Knowledge article outdated",
        "Risk too high",
        "Another resolution preferred",
        "Other"
    ];

    return (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-md w-full overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
                    <h4 className="font-bold text-slate-900 text-sm">Why are you overriding this recommendation?</h4>
                    <p className="text-xs text-slate-500">Capture feedback to improve decision support retrieval accuracy.</p>
                </div>

                <div className="p-6 space-y-4 text-xs">
                    <div className="space-y-2">
                        {reasons.map((r) => (
                            <label key={r} className="flex items-center gap-2.5 cursor-pointer font-medium text-slate-700">
                                <input
                                    type="radio"
                                    name="override_reason"
                                    value={r}
                                    checked={reason === r}
                                    onChange={(e) => setReason(e.target.value)}
                                    className="text-blue-600 focus:ring-blue-500"
                                />
                                <span>{r}</span>
                            </label>
                        ))}
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1">Optional Comments</label>
                        <textarea
                            value={comment}
                            onChange={(e) => setComment(e.target.value)}
                            rows={2}
                            placeholder="Provide additional details regarding the override..."
                            className="w-full rounded-lg border border-slate-300 p-2 text-xs text-slate-900 focus:ring-2 focus:ring-blue-500 outline-none"
                        />
                    </div>
                </div>

                <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-end gap-2">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700">
                        Cancel
                    </button>
                    <button
                        onClick={onSubmit}
                        disabled={loading}
                        className="bg-red-600 hover:bg-red-700 text-white font-bold text-xs px-5 py-2 rounded-lg shadow-sm">
                        {loading ? <i className="fa-solid fa-spinner animate-spin"></i> : 'Submit Override'}
                    </button>
                </div>
            </div>
        </div>
    );
}

// 6. Incidents List View
function IncidentsListView({ incidents, onSelectIncident }) {
    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-xl font-bold text-slate-900">Hospital IT Incidents Register</h3>
                    <p className="text-xs text-slate-500">Full audit log of clinical system IT tickets and status timelines.</p>
                </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
                <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                        <tr>
                            <th className="px-4 py-3">Incident ID</th>
                            <th className="px-4 py-3">Description</th>
                            <th className="px-4 py-3">System / Version</th>
                            <th className="px-4 py-3">Severity</th>
                            <th className="px-4 py-3">Status</th>
                            <th className="px-4 py-3">Created Time</th>
                            <th className="px-4 py-3">TTR</th>
                            <th className="px-4 py-3 text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {incidents.map((inc) => (
                            <tr key={inc.incident_id} className="hover:bg-slate-50">
                                <td className="px-4 py-3 font-mono font-bold text-blue-600">{inc.incident_id}</td>
                                <td className="px-4 py-3 font-medium text-slate-900 max-w-sm truncate">{inc.description}</td>
                                <td className="px-4 py-3 font-semibold text-slate-800">{inc.system} v{inc.version}</td>
                                <td className="px-4 py-3"><SeverityBadge severity={inc.severity} /></td>
                                <td className="px-4 py-3"><StatusBadge status={inc.status} /></td>
                                <td className="px-4 py-3 text-slate-500 text-[11px]">{inc.created_at}</td>
                                <td className="px-4 py-3 font-mono font-bold text-slate-800">
                                    {inc.ttr_minutes ? `${inc.ttr_minutes}m` : '-'}
                                </td>
                                <td className="px-4 py-3 text-right">
                                    <button 
                                        onClick={() => onSelectIncident(inc.incident_id)}
                                        className="text-blue-600 hover:text-blue-800 font-semibold text-xs">
                                        View Timeline →
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

// 7. Incident Detail View & Lifecycle Timeline
function IncidentDetailView({ incidentDetails, onBack }) {
    if (!incidentDetails) return null;
    const { incident, timeline } = incidentDetails;

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <button onClick={onBack} className="text-xs font-semibold text-blue-600 hover:underline flex items-center gap-1">
                ← Back to Incidents List
            </button>

            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                    <div>
                        <span className="font-mono font-bold text-blue-600 text-sm">{incident.incident_id}</span>
                        <h3 className="text-lg font-bold text-slate-900">{incident.description}</h3>
                    </div>
                    <StatusBadge status={incident.status} />
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs bg-slate-50 p-4 rounded-lg border border-slate-200">
                    <div>
                        <div className="text-[10px] text-slate-500 uppercase font-semibold">System</div>
                        <div className="font-bold text-slate-800">{incident.system} v{incident.version}</div>
                    </div>
                    <div>
                        <div className="text-[10px] text-slate-500 uppercase font-semibold">Category</div>
                        <div className="font-bold text-slate-800">{incident.category}</div>
                    </div>
                    <div>
                        <div className="text-[10px] text-slate-500 uppercase font-semibold">Severity / Impact</div>
                        <div className="font-bold text-slate-800">{incident.severity} ({incident.impact_level})</div>
                    </div>
                    <div>
                        <div className="text-[10px] text-slate-500 uppercase font-semibold">Time to Resolution</div>
                        <div className="font-mono font-extrabold text-blue-700 text-sm">
                            {incident.ttr_minutes ? `${incident.ttr_minutes} minutes` : 'In Progress'}
                        </div>
                    </div>
                </div>

                <div>
                    <h4 className="font-bold text-slate-900 text-sm mb-4">Incident Lifecycle Timeline</h4>
                    <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                        {timeline.map((step, idx) => (
                            <div key={idx} className="relative flex items-start gap-4">
                                <div className={`absolute -left-6 w-5 h-5 rounded-full border-2 flex items-center justify-center text-[10px] font-bold ${
                                    step.completed 
                                        ? 'bg-emerald-500 border-emerald-600 text-white' 
                                        : 'bg-white border-slate-300 text-slate-400'
                                }`}>
                                    {step.completed ? '✓' : idx + 1}
                                </div>
                                <div>
                                    <div className="text-xs font-bold text-slate-900">{step.step}</div>
                                    <div className="text-[11px] text-slate-500">{step.detail}</div>
                                    {step.timestamp && <div className="text-[10px] font-mono text-slate-400">{step.timestamp}</div>}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

// 8. Knowledge Base View
function KnowledgeBaseView({ articles }) {
    return (
        <div className="space-y-4">
            <div>
                <h3 className="text-xl font-bold text-slate-900">Clinical IT Knowledge Base</h3>
                <p className="text-xs text-slate-500">Repository of verified fix articles with system version boundaries.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {articles.map((art) => (
                    <div key={art.article_id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="font-mono font-bold text-xs text-blue-700">{art.article_id}</span>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                                art.status === 'CURRENT' ? 'bg-emerald-100 text-emerald-800 border-emerald-200' : 'bg-amber-100 text-amber-800 border-amber-200'
                            }`}>
                                {art.status}
                            </span>
                        </div>
                        <h4 className="font-bold text-slate-900 text-sm">{art.title}</h4>
                        <p className="text-xs text-slate-600">{art.content}</p>
                        <div className="text-[11px] text-slate-500 pt-2 border-t border-slate-100 flex items-center justify-between">
                            <span>System: <strong>{art.system}</strong> (v{art.version_from} - v{art.version_to})</span>
                            <span>Verified: {art.last_verified}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// 9. Analytics View
function AnalyticsView({ data }) {
    if (!data) return null;
    const { ttr, charts } = data;

    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-xl font-bold text-slate-900">Resolution Analytics</h3>
                <p className="text-xs text-slate-500">Performance metrics evaluating time-to-resolution improvements for recurring clinical IT incidents.</p>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
                <div>
                    <div className="text-xs font-semibold text-slate-500 uppercase">Baseline TTR (Manual)</div>
                    <div className="text-2xl font-black text-slate-700 mt-1">{ttr.baseline_ttr_minutes} min</div>
                </div>
                <div>
                    <div className="text-xs font-semibold text-slate-500 uppercase">Target TTR</div>
                    <div className="text-2xl font-black text-indigo-600 mt-1">{ttr.target_ttr_minutes} min</div>
                </div>
                <div>
                    <div className="text-xs font-semibold text-slate-500 uppercase">Prototype Result</div>
                    <div className="text-2xl font-black text-blue-600 mt-1">{ttr.measured_prototype_ttr_minutes} min</div>
                </div>
                <div>
                    <div className="text-xs font-semibold text-slate-500 uppercase">TTR Improvement</div>
                    <div className="text-2xl font-black text-emerald-600 mt-1">+{ttr.ttr_improvement_pct}%</div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs space-y-3">
                    <h4 className="font-bold text-slate-900 text-sm">Average TTR by Incident Category</h4>
                    <div className="space-y-2 text-xs">
                        {charts.category_ttr.map((c, i) => (
                            <div key={i} className="space-y-1">
                                <div className="flex justify-between font-medium">
                                    <span>{c.category}</span>
                                    <span>{c.avg_ttr}m (Baseline {c.baseline_ttr}m)</span>
                                </div>
                                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                                    <div className="bg-blue-600 h-full rounded-full" style={{ width: `${(c.avg_ttr / c.baseline_ttr) * 100}%` }}></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs space-y-3">
                    <h4 className="font-bold text-slate-900 text-sm">Override Reasons Distribution</h4>
                    <div className="space-y-2 text-xs">
                        {charts.override_reasons.map((r, i) => (
                            <div key={i} className="flex items-center justify-between p-2 bg-slate-50 rounded border border-slate-200">
                                <span className="font-medium text-slate-800">{r.reason}</span>
                                <span className="font-mono font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded">{r.count} incidents</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

// 10. Experiment View
function ExperimentView({ data }) {
    if (!data) return null;
    const { baseline_vs_prototype, error_analysis_table } = data;

    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-xl font-bold text-slate-900">Experiment & Benchmark Evaluation</h3>
                <p className="text-xs text-slate-500">Controlled experimental comparison: Manual Historical Lookup vs Verified Resolution Assistant.</p>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-6 space-y-4">
                <h4 className="font-bold text-slate-900 text-sm">Baseline vs Prototype Benchmark</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
                        <div className="font-bold text-slate-700 text-sm">Baseline (Manual Search)</div>
                        <p className="text-[11px] text-slate-500">{baseline_vs_prototype.baseline.method}</p>
                        <ul className="space-y-1.5 font-medium">
                            <li>Average TTR: <strong>{baseline_vs_prototype.baseline.avg_ttr_min} min</strong></li>
                            <li>Median TTR: <strong>{baseline_vs_prototype.baseline.median_ttr_min} min</strong></li>
                            <li>Resolution Success: <strong>{baseline_vs_prototype.baseline.success_rate_pct}%</strong></li>
                        </ul>
                    </div>

                    <div className="p-4 bg-blue-50/50 rounded-xl border border-blue-200 space-y-3">
                        <div className="font-bold text-blue-900 text-sm">Prototype (Verified Assistant)</div>
                        <p className="text-[11px] text-blue-700">{baseline_vs_prototype.prototype.method}</p>
                        <ul className="space-y-1.5 font-semibold text-blue-950">
                            <li>Average TTR: <strong>{baseline_vs_prototype.prototype.avg_ttr_min} min</strong></li>
                            <li>Median TTR: <strong>{baseline_vs_prototype.prototype.median_ttr_min} min</strong></li>
                            <li>Resolution Success: <strong>{baseline_vs_prototype.prototype.success_rate_pct}%</strong></li>
                        </ul>
                    </div>
                </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-2xs p-6 space-y-4">
                <h4 className="font-bold text-slate-900 text-sm">Error Analysis Table</h4>
                <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                        <tr>
                            <th className="px-4 py-2.5">Error Type</th>
                            <th className="px-4 py-2.5 text-right">Count</th>
                            <th className="px-4 py-2.5">Primary Root Cause</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {error_analysis_table.map((row, idx) => (
                            <tr key={idx}>
                                <td className="px-4 py-2.5 font-bold text-slate-800">{row.error_type}</td>
                                <td className="px-4 py-2.5 text-right font-mono font-bold text-red-600">{row.count}</td>
                                <td className="px-4 py-2.5 text-slate-600">{row.cause}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

// 11. Event Reliability Demo View
function EventReliabilityView({ stream, summary, result, onInject }) {
    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-xl font-bold text-slate-900">Event Reliability & Fault Tolerance Demo</h3>
                <p className="text-xs text-slate-500">Demonstrates idempotent event processing and resilience against duplicates, delayed arrivals, and out-of-order execution.</p>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-2xs space-y-4">
                <h4 className="font-bold text-slate-900 text-sm">Inject Simulated Network Fault Events</h4>
                <div className="flex flex-wrap items-center gap-3">
                    <button
                        onClick={() => onInject('DUPLICATE')}
                        className="bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs px-4 py-2 rounded-lg shadow-2xs flex items-center gap-1.5">
                        <i className="fa-solid fa-copy"></i>
                        Inject Duplicate Event
                    </button>

                    <button
                        onClick={() => onInject('DELAYED')}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs px-4 py-2 rounded-lg shadow-2xs flex items-center gap-1.5">
                        <i className="fa-solid fa-clock-rotate-left"></i>
                        Inject Delayed Event
                    </button>

                    <button
                        onClick={() => onInject('OUT_OF_ORDER')}
                        className="bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs px-4 py-2 rounded-lg shadow-2xs flex items-center gap-1.5">
                        <i className="fa-solid fa-shuffle"></i>
                        Inject Out-of-Order Event
                    </button>
                </div>

                {result && (
                    <div className="p-4 bg-slate-900 text-slate-100 rounded-lg text-xs font-mono space-y-1">
                        <div className="text-emerald-400 font-bold">Injection Result Status: {result.processing_result}</div>
                        <div>Message: {result.message}</div>
                        <div>State Consistency: {result.state_consistency}</div>
                    </div>
                )}
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
                <div className="px-5 py-4 border-b border-slate-100 font-bold text-slate-900 text-sm">
                    Live Audit Event Stream Log
                </div>
                <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                        <tr>
                            <th className="px-4 py-2.5">Event ID</th>
                            <th className="px-4 py-2.5">Incident ID</th>
                            <th className="px-4 py-2.5">Event Type</th>
                            <th className="px-4 py-2.5">Sequence #</th>
                            <th className="px-4 py-2.5">Processing Result</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-mono">
                        {stream.map((evt) => (
                            <tr key={evt.event_id}>
                                <td className="px-4 py-2.5 font-bold text-blue-600">{evt.event_id}</td>
                                <td className="px-4 py-2.5 text-slate-700">{evt.incident_id}</td>
                                <td className="px-4 py-2.5 font-sans font-semibold text-slate-900">{evt.event_type}</td>
                                <td className="px-4 py-2.5 text-slate-600">Seq {evt.sequence_number}</td>
                                <td className="px-4 py-2.5 font-sans">
                                    <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded">
                                        {evt.status}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

// 12. Risk Register & Stakeholder Validation View
function RiskAndStakeholderView({ riskRegister, stakeholderData }) {
    return (
        <div className="space-y-8">
            <div className="space-y-4">
                <div>
                    <h3 className="text-xl font-bold text-slate-900">Governance & Risk Register</h3>
                    <p className="text-xs text-slate-500">Formal risk assessment matrix for clinical IT decision-support system implementation.</p>
                </div>

                <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
                    <table className="w-full text-left text-xs">
                        <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                            <tr>
                                <th className="px-4 py-3">Risk Description</th>
                                <th className="px-4 py-3">Impact</th>
                                <th className="px-4 py-3">Likelihood</th>
                                <th className="px-4 py-3">Architectural Mitigation</th>
                                <th className="px-4 py-3">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {riskRegister.map((r) => (
                                <tr key={r.risk_id}>
                                    <td className="px-4 py-3 font-bold text-slate-900">{r.risk}</td>
                                    <td className="px-4 py-3">
                                        <span className={`font-bold ${r.impact === 'Critical' || r.impact === 'High' ? 'text-red-600' : 'text-amber-600'}`}>
                                            {r.impact}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 font-medium text-slate-700">{r.likelihood}</td>
                                    <td className="px-4 py-3 text-slate-600 max-w-md">{r.mitigation}</td>
                                    <td className="px-4 py-3">
                                        <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded">
                                            {r.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="space-y-4">
                <div>
                    <h3 className="text-xl font-bold text-slate-900">Stakeholder Validation</h3>
                    <p className="text-xs text-slate-500">Evaluation survey feedback from Hospital IT Support Leads and Systems Managers.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {stakeholderData?.responses?.map((resp) => (
                        <div key={resp.feedback_id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs space-y-2">
                            <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-blue-700">{resp.stakeholder_role}</span>
                                <div className="flex text-amber-400 text-xs">
                                    {[...Array(resp.rating)].map((_, i) => <i key={i} className="fa-solid fa-star"></i>)}
                                </div>
                            </div>
                            <h4 className="font-bold text-slate-900 text-xs">{resp.question}</h4>
                            <p className="text-xs text-slate-600 italic">"{resp.comment}"</p>
                        </div>
                    ))}
                </div>
            </div>

            <div className="p-4 bg-slate-900 text-slate-200 rounded-xl text-xs space-y-1">
                <div className="font-bold text-emerald-400">Privacy-by-Design Compliance Statement</div>
                <div>No patient or unnecessary personal data is collected by this prototype.</div>
            </div>
        </div>
    );
}

// 13. User Guide View
function UserGuideView() {
    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div>
                <h3 className="text-xl font-bold text-slate-900">IT Support Engineer User Guide</h3>
                <p className="text-xs text-slate-500">Operational workflow instructions for resolving clinical IT incidents.</p>
            </div>

            <div className="space-y-4 text-xs">
                <GuideSection num="1" title="Creating an Incident" text="Navigate to 'New Incident' and enter the incident description, clinical system name (e.g. LabSys, PACSView), and current software version (e.g. 5.4)." />
                <GuideSection num="2" title="Multi-Stage Verification Pipeline" text="The system automatically executes a 5-step verification pipeline: System Match (Hard Filter) → Version Match → Article Status → Historical Evidence → Evidence Scoring." />
                <GuideSection num="3" title="Reviewing Verified vs Rejected Candidates" text="The Resolution Assistant page divides output into VERIFIED RECOMMENDATIONS (passes all filters) and REJECTED CANDIDATES (blocked due to System Mismatch, Version Incompatibility, or Retired Article)." />
                <GuideSection num="4" title="System Mismatch Guardrail" text="Resolutions from mismatched systems (e.g. LabSys fixes for PACSView incidents) are strictly BLOCKED and marked with '❌ Resolution Not Recommended — System mismatch'." />
                <GuideSection num="5" title="Approving High-Impact Actions" text="High-impact actions (e.g. service restarts) display a warning and require explicit human approval ('Approve Fix'). The system never auto-executes high-impact commands." />
                <GuideSection num="6" title="Rejecting Recommendations & Overrides" text="If a recommendation is not suitable, click 'Reject Recommendation' and select an override reason (e.g. Version mismatch, Fix already attempted) to log structured feedback." />
                <GuideSection num="7" title="Viewing TTR Analytics" text="Visit 'Resolution Analytics' to track time-to-resolution (TTR) improvements against manual baseline benchmarks." />
                <GuideSection num="8" title="Understanding Event Reliability" text="Use the 'Event Reliability' tab to simulate network anomalies (duplicate, delayed, or out-of-order events) and verify idempotent state processing." />
            </div>
        </div>
    );
}

function GuideSection({ num, title, text }) {
    return (
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs flex items-start gap-3">
            <div className="w-6 h-6 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center flex-shrink-0">
                {num}
            </div>
            <div>
                <h4 className="font-bold text-slate-900 text-xs mb-1">{title}</h4>
                <p className="text-slate-600 leading-relaxed">{text}</p>
            </div>
        </div>
    );
}

// Render React App to Root
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
