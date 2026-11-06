// KratosSecure Hospital Digital Twin Client Engine (Phase 1 & Phase 2)
let currentActor = "dr_elena_vance";
let cachedPatient = null;
let currentModalTab = "demographics";
let testCasesCache = [];

const ACTOR_ROLES = {
  dr_elena_vance: "Doctor (IPD)",
  dr_marcus_brody: "Doctor (ED)",
  nurse_sarah_connor: "Nurse (ICU)",
  nurse_david_kim: "Nurse (IPD)",
  tech_rachel_zane: "Lab Technician",
  pharm_james_wilson: "Pharmacist",
  billing_arthur_dent: "Billing Officer",
  mro_diana_prince: "Medical Records",
  admin_sterling_archer: "Hospital Admin",
  it_elliot_alderson: "IT Administrator",
  sec_john_connor: "Security Officer",
  agent_kratos_ai: "Healthcare AI Agent",
  adversarial_infiltrator: "Adversarial Agent"
};

function getHeaders() {
  return {
    "Content-Type": "application/json",
    "X-Actor-Id": currentActor,
    "X-Purpose-Of-Use": "treatment"
  };
}

function showToast(message, isError = false) {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = "toast-msg";
  toast.style.borderColor = isError ? "var(--accent-rose)" : "var(--accent-cyan)";
  toast.innerHTML = `<span>${isError ? '⚠️' : 'ℹ️'}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4500);
}

// Actor Switcher
window.switchActor = function(actorId) {
  currentActor = actorId;
  const roleText = ACTOR_ROLES[actorId] || actorId;
  const badge = document.getElementById("actorRoleBadge");
  badge.textContent = roleText;
  
  if (actorId.includes("adv")) {
    badge.className = "actor-badge badge-critical";
  } else if (actorId.includes("ai")) {
    badge.className = "actor-badge badge-degraded";
  } else {
    badge.className = "actor-badge badge-operational";
  }

  showToast(`Switched actor identity to: ${roleText}. RBAC permissions updated.`);
  loadAllData();
};

// Tab Switcher
window.switchTab = function(tabId, el) {
  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".content-pane").forEach(pane => pane.classList.remove("active"));

  if (el) el.classList.add("active");
  const targetPane = document.getElementById(`pane-${tabId}`);
  if (targetPane) targetPane.classList.add("active");

  if (tabId === "adversarial" && testCasesCache.length === 0) loadAdversarialScenarios();
  if (tabId === "analytics") loadAnalytics();
  if (tabId === "library" && testCasesCache.length === 0) loadAdversarialScenarios();
  if (tabId === "experiments") window.loadExperimentComparison();
  if (tabId === "counterfactual") window.loadBottleneckAnalysis();
  if (tabId === "reports") window.loadExecutedExperimentsList();
};

// Initial Boot Data Loading
async function loadAllData() {
  await Promise.all([
    loadOverview(),
    loadInfrastructure(),
    loadPatients(),
    loadStaff(),
    loadInventory(),
    loadScenarios(),
    loadAuditEvents(),
    loadCanaries(),
    loadAgentTools(),
    loadAdversarialScenarios(),
    loadAnalytics()
  ]);
}

// -------------------------------------------------------------
// OVERVIEW & INFRASTRUCTURE
// -------------------------------------------------------------
async function loadOverview() {
  try {
    const res = await fetch("/api/v1/operations/summary", { headers: getHeaders() });
    if (res.ok) {
      const data = await res.json();
      document.getElementById("kpiTotalBeds").textContent = data.total_beds;
      document.getElementById("kpiOccupiedBeds").textContent = data.occupied_beds;
      document.getElementById("kpiOccupancyRate").textContent = `${data.occupancy_rate_percentage}%`;
      document.getElementById("kpiOccupancyFill").style.width = `${data.occupancy_rate_percentage}%`;

      document.getElementById("kpiIcuBeds").textContent = data.total_icu_beds;
      document.getElementById("kpiOccupiedIcu").textContent = data.occupied_icu_beds;
      document.getElementById("kpiAvailableIcu").textContent = data.available_icu_beds;
      document.getElementById("kpiIcuFill").style.width = `${data.icu_occupancy_rate_percentage}%`;

      document.getElementById("kpiEdWait").textContent = `${data.emergency_wait_time_minutes} min`;
      document.getElementById("kpiEdActive").textContent = `${data.emergency_admissions_active} Active Patients`;
      document.getElementById("kpiAmbulances").textContent = `${data.available_ambulances} / ${data.total_ambulances}`;
    }

    const subRes = await fetch("/api/v1/system/status", { headers: getHeaders() });
    if (subRes.ok) {
      const subs = await subRes.json();
      const container = document.getElementById("subsystemsContainer");
      container.innerHTML = subs.map(s => {
        const dot = s.status === 'operational' ? 'dot-green' : (s.status === 'degraded' ? 'dot-amber' : 'dot-red');
        const badgeClass = s.status === 'operational' ? 'badge-operational' : (s.status === 'degraded' ? 'badge-degraded' : 'badge-offline');
        return `
          <div class="dept-tile">
            <div class="dept-top">
              <span class="dept-title">${s.name}</span>
              <span class="badge ${badgeClass}">${s.status}</span>
            </div>
            <div class="dept-meta">
              <span>Code: <code>${s.system_code}</code></span>
              <span><span class="status-dot ${dot}"></span> Latency: ${s.latency_ms}ms</span>
            </div>
            ${s.details ? `<div style="font-size: 11px; color: var(--accent-amber); margin-top: 6px;">${s.details}</div>` : ''}
          </div>
        `;
      }).join("");
    }
  } catch (err) {
    console.error("Overview error", err);
  }
}

async function loadInfrastructure() {
  try {
    const res = await fetch("/api/v1/operations/departments", { headers: getHeaders() });
    if (!res.ok) return;
    const depts = await res.json();

    const renderDeptTile = (d) => {
      const bClass = d.status === 'operational' ? 'badge-operational' : (d.status === 'emergency_mode' ? 'badge-critical' : 'badge-degraded');
      return `
        <div class="dept-tile">
          <div class="dept-top">
            <span class="dept-title">${d.name}</span>
            <span class="badge ${bClass}">${d.status}</span>
          </div>
          <div class="dept-meta">
            <span>Floor: ${d.floor}</span>
            <span>Beds: ${d.total_beds > 0 ? d.total_beds : 'N/A'}</span>
          </div>
          <div class="dept-meta" style="margin-top: 4px;">
            <span>Workload: <strong>${d.current_workload}</strong></span>
            <span>Wait: ${d.wait_time_minutes}m</span>
          </div>
        </div>
      `;
    };

    document.getElementById("buildingADepts").innerHTML = depts.filter(d => d.building.includes("Building A")).map(renderDeptTile).join("");
    document.getElementById("buildingBDepts").innerHTML = depts.filter(d => d.building.includes("Building B")).map(renderDeptTile).join("");
    document.getElementById("buildingCDepts").innerHTML = depts.filter(d => d.building.includes("Building C")).map(renderDeptTile).join("");
  } catch (err) {
    console.error("Infra error", err);
  }
}

// -------------------------------------------------------------
// PHASE 2: HOSA AGENT INTERACTION
// -------------------------------------------------------------
async function loadAgentTools() {
  try {
    const res = await fetch("/api/v1/agent/tools");
    if (!res.ok) return;
    const tools = await res.json();
    const container = document.getElementById("agentToolsList");
    container.innerHTML = Object.values(tools).map(t => `
      <div style="padding: 6px 0; border-bottom: 1px solid var(--border-color);">
        <div style="display: flex; justify-content: space-between;">
          <strong style="color: var(--accent-cyan); font-family: var(--font-mono);">${t.name}</strong>
          ${t.requires_human_approval ? '<span class="badge badge-critical" style="font-size: 8px;">HUMAN SIGN-OFF</span>' : '<span class="badge badge-operational" style="font-size: 8px;">AUTO</span>'}
        </div>
        <p style="color: var(--text-muted); font-size: 10px; margin-top: 2px;">${t.description}</p>
      </div>
    `).join("");
  } catch (err) {
    console.error("Tools load error", err);
  }
}

window.sendAgentPrompt = async function() {
  const input = document.getElementById("agentPromptInput");
  const prompt = input.value.trim();
  if (!prompt) return;

  const patientId = parseInt(document.getElementById("agentPatientContextSelect").value) || 1;
  const chatBox = document.getElementById("agentChatBox");

  // Append user bubble
  chatBox.innerHTML += `
    <div class="message-bubble msg-user">
      <strong>${ACTOR_ROLES[currentActor] || currentActor}:</strong><br>
      ${prompt}
    </div>
  `;
  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const res = await fetch("/api/v1/agent/hosa/prompt", {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({
        user_prompt: prompt,
        requesting_actor: currentActor,
        purpose_of_use: "treatment",
        active_patient_id: patientId
      })
    });

    const data = await res.json();

    // Format agent bubble with tool decision tags
    let toolBadges = "";
    if (data.tool_invocations && data.tool_invocations.length > 0) {
      toolBadges = data.tool_invocations.map(inv => {
        const oClass = inv.outcome === 'ALLOW' ? 'badge-operational' : (inv.outcome === 'REQUIRE_HUMAN_APPROVAL' ? 'badge-degraded' : 'badge-critical');
        return `<span class="badge ${oClass}" style="margin-right: 4px; font-size: 10px;">${inv.tool_name}: ${inv.outcome}</span>`;
      }).join("");
    }

    chatBox.innerHTML += `
      <div class="message-bubble msg-agent">
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
          <strong style="color: var(--accent-cyan);">HOSA Support Agent:</strong>
          <div>${toolBadges}</div>
        </div>
        <div style="white-space: pre-wrap;">${data.content}</div>
        ${data.policy_violations_prevented.length > 0 ? `
          <div style="margin-top: 8px; font-size: 11px; color: var(--accent-emerald);">
            🛡️ Guardrail Protected: ${data.policy_violations_prevented.join(", ")}
          </div>
        ` : ''}
      </div>
    `;
    chatBox.scrollTop = chatBox.scrollHeight;
    loadAuditEvents();
  } catch (err) {
    console.error("Agent error", err);
    showToast("Error communicating with HOSA agent", true);
  }
};

// -------------------------------------------------------------
// PHASE 2: AAVA ADVERSARIAL SUITE & TRACES
// -------------------------------------------------------------
async function loadAdversarialScenarios() {
  try {
    const res = await fetch("/api/v1/agent/taxonomy");
    if (!res.ok) return;
    const data = await res.json();
    testCasesCache = data.test_cases;

    // Populate Select Box
    const select = document.getElementById("adversarialScenarioSelect");
    select.innerHTML = testCasesCache.map(tc => `
      <option value="${tc.test_id}">[${tc.test_id}] ${tc.name} (${tc.severity})</option>
    `).join("");

    select.onchange = () => {
      const selected = testCasesCache.find(t => t.test_id === select.value);
      if (selected) {
        document.getElementById("activeTestPreview").innerHTML = `
          <strong>Category:</strong> ${selected.category_title} | <strong>Objective:</strong> ${selected.attack_objective}<br>
          <strong>Simulated Payload:</strong> <code>"${selected.user_prompt}"</code>
        `;
      }
    };
    select.onchange();

    // Populate Test Case Library Table
    renderLibraryTable(testCasesCache);
  } catch (err) {
    console.error("Taxonomy error", err);
  }
}

function renderLibraryTable(cases) {
  const tbody = document.getElementById("testLibraryTableBody");
  tbody.innerHTML = cases.map(tc => {
    const sClass = tc.severity === 'CRITICAL' ? 'badge-critical' : (tc.severity === 'HIGH' ? 'badge-degraded' : 'badge-operational');
    return `
      <tr>
        <td><strong style="color: var(--accent-cyan); font-family: var(--font-mono);">${tc.test_id}</strong></td>
        <td><strong>${tc.name}</strong></td>
        <td><span class="badge badge-info">${tc.category_title}</span></td>
        <td><span class="badge ${sClass}">${tc.severity}</span></td>
        <td><code>${tc.requesting_actor}</code></td>
        <td style="max-width: 320px; font-size: 12px; color: var(--text-secondary);">${tc.attack_objective}</td>
        <td>
          <button class="patient-action-btn" onclick="window.runSingleTest('${tc.test_id}')">Run Test ⚡</button>
        </td>
      </tr>
    `;
  }).join("");
}

window.filterLibrary = function() {
  const cat = document.getElementById("libraryCategoryFilter").value;
  const q = document.getElementById("librarySearchInput").value.toLowerCase();

  const filtered = testCasesCache.filter(tc => {
    const matchCat = !cat || tc.category === cat;
    const matchQ = !q || tc.name.toLowerCase().includes(q) || tc.test_id.toLowerCase().includes(q) || tc.attack_objective.toLowerCase().includes(q);
    return matchCat && matchQ;
  });
  renderLibraryTable(filtered);
};

window.runSelectedAdversarialTest = async function() {
  const testId = document.getElementById("adversarialScenarioSelect").value;
  await window.runSingleTest(testId);
};

window.runSingleTest = async function(testId) {
  showToast(`AAVA dispatching attack vector: ${testId}...`);
  const statusBadge = document.getElementById("traceStatusBadge");
  statusBadge.textContent = "Execution In Progress...";

  try {
    const res = await fetch(`/api/v1/agent/aava/run-test/${testId}`, { method: "POST" });
    if (!res.ok) {
      showToast("Error executing adversarial test", true);
      return;
    }
    const trace = await res.json();
    renderExecutionTimeline(trace);

    if (trace.attack_succeeded) {
      showToast(`⚠️ TEST FAILED: ${testId} attack succeeded!`, true);
      statusBadge.innerHTML = `<span class="badge badge-critical">FAILED (BREACH)</span>`;
    } else {
      showToast(`✅ TEST PASSED: ${testId} attack contained!`);
      statusBadge.innerHTML = `<span class="badge badge-operational">PASSED (CONTAINED)</span>`;
    }
    loadAnalytics();
    loadAuditEvents();
  } catch (err) {
    console.error("Test execution error", err);
    showToast("Error running test case", true);
  }
};

function renderExecutionTimeline(trace) {
  const container = document.getElementById("executionTimeline");
  if (!trace.execution_steps || trace.execution_steps.length === 0) {
    container.innerHTML = `<p>No timeline steps available.</p>`;
    return;
  }

  container.innerHTML = trace.execution_steps.map(step => {
    let iconClass = "icon-req";
    let iconSymbol = "📝";

    if (step.step_type === "TOOL_INVOCATION") { iconSymbol = "⚙️"; iconClass = "icon-req"; }
    else if (step.step_type === "GATEWAY_DECISION") {
      const outcome = step.metadata.outcome || "ALLOW";
      if (outcome === "ALLOW") { iconSymbol = "✓"; iconClass = "icon-allow"; }
      else if (outcome === "REQUIRE_HUMAN_APPROVAL") { iconSymbol = "⏳"; iconClass = "icon-req"; }
      else { iconSymbol = "✕"; iconClass = "icon-deny"; }
    }
    else if (step.step_type === "AAVA_OBSERVATION") { iconSymbol = "🎯"; iconClass = "icon-obs"; }
    else if (step.step_type === "EVALUATION") {
      iconSymbol = trace.attack_succeeded ? "🚨" : "🛡️";
      iconClass = trace.attack_succeeded ? "icon-deny" : "icon-allow";
    }

    return `
      <div class="timeline-node">
        <div class="timeline-icon ${iconClass}">${iconSymbol}</div>
        <div class="timeline-body">
          <div class="timeline-step-title">
            <span>Step ${step.step_number}: ${step.title}</span>
            <span style="font-size: 11px; color: var(--text-muted);">${step.timestamp ? step.timestamp.substring(11, 19) : ''}</span>
          </div>
          <div class="timeline-step-desc">${step.description}</div>
          ${Object.keys(step.metadata || {}).length > 0 ? `
            <pre style="background: #060911; padding: 8px; border-radius: 4px; margin-top: 6px; font-size: 11px; font-family: var(--font-mono); overflow-x: auto;">${JSON.stringify(step.metadata, null, 2)}</pre>
          ` : ''}
        </div>
      </div>
    `;
  }).join("");
}

window.runFullTestSuite = async function() {
  if (!confirm("Run all 20 healthcare adversarial test cases sequentially? This evaluates full hospital resilience.")) return;
  showToast("Running complete 20-test validation suite... please wait.");

  try {
    const res = await fetch("/api/v1/agent/aava/run-suite", { method: "POST" });
    const data = await res.json();
    showToast(`Suite Execution Complete: ${data.passed_count} Passed / ${data.failed_count} Failed out of ${data.total_executed} tests!`);
    loadAnalytics();
    loadAuditEvents();
    if (data.results && data.results.length > 0) {
      renderExecutionTimeline(data.results[data.results.length - 1]);
    }
  } catch (err) {
    console.error("Suite error", err);
    showToast("Error running test suite", true);
  }
};

window.runAdaptiveProbe = async function() {
  showToast("AAVA synthesizing novel adaptive attack probe...");
  try {
    const res = await fetch("/api/v1/agent/aava/adaptive-probe", { method: "POST" });
    const trace = await res.json();
    renderExecutionTimeline(trace);
    showToast(`Adaptive probe finished: ${trace.status}`);
    loadAnalytics();
  } catch (err) {
    console.error("Adaptive error", err);
  }
};

// -------------------------------------------------------------
// PHASE 2: SECURITY ANALYTICS
// -------------------------------------------------------------
async function loadAnalytics() {
  try {
    const res = await fetch("/api/v1/agent/analytics");
    if (!res.ok) return;
    const data = await res.json();
    if (!data.summary) return;

    document.getElementById("metricAsr").textContent = `${data.summary.attack_success_rate_percentage}%`;
    document.getElementById("metricAsr").style.color = data.summary.attack_success_rate_percentage === 0 ? "var(--accent-emerald)" : "var(--accent-rose)";

    document.getElementById("metricUtility").textContent = `${data.summary.agent_utility_score} / 100`;
    document.getElementById("metricCompletion").textContent = data.agent_behavior_metrics.legitimate_task_completion_rate;
    document.getElementById("metricLatency").textContent = `${data.operational_metrics.avg_security_detection_latency_ms} ms`;

    // Render Heatmap
    const heatmap = document.getElementById("analyticsHeatmap");
    const catKeys = Object.keys(data.category_distribution || {});
    if (catKeys.length === 0) {
      heatmap.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">No test runs recorded yet. Execute test cases to view category resilience.</p>`;
      return;
    }

    heatmap.innerHTML = catKeys.map(cat => {
      const d = data.category_distribution[cat];
      const asr = d.total > 0 ? roundNumber((d.failed / d.total) * 100, 1) : 0;
      const bColor = asr === 0 ? "var(--accent-emerald)" : "var(--accent-rose)";
      return `
        <div class="heatmap-cell" style="border-top: 3px solid ${bColor};">
          <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted);">${cat}</div>
          <div class="heatmap-score" style="color: ${bColor};">${d.passed} / ${d.total}</div>
          <div style="font-size: 12px; color: var(--text-secondary);">Passed (${100 - asr}% Held)</div>
        </div>
      `;
    }).join("");
  } catch (err) {
    console.error("Analytics error", err);
  }
}

function roundNumber(num, dec) {
  return Math.round(num * Math.pow(10, dec)) / Math.pow(10, dec);
}

// -------------------------------------------------------------
// PATIENT DIRECTORY & MODAL
// -------------------------------------------------------------
window.searchPatients = async function() {
  const q = document.getElementById("patientSearchInput").value.trim();
  loadPatients(q);
};

async function loadPatients(query = "") {
  try {
    const url = query ? `/api/v1/patients?query=${encodeURIComponent(query)}&limit=30` : `/api/v1/patients?limit=30`;
    const res = await fetch(url, { headers: getHeaders() });
    const tbody = document.getElementById("patientsTableBody");

    if (res.status === 403) {
      const err = await res.json();
      tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--accent-rose); padding: 24px;">🚫 ${err.detail}</td></tr>`;
      return;
    }
    if (!res.ok) return;
    const patients = await res.json();

    tbody.innerHTML = patients.map(p => `
      <tr>
        <td><strong style="font-family: var(--font-mono); color: var(--accent-cyan);">${p.mrn}</strong></td>
        <td><strong>${p.first_name} ${p.last_name}</strong></td>
        <td>${p.dob}</td>
        <td>${p.gender}</td>
        <td><span class="badge" style="background: rgba(244,63,94,0.15); color: #fb7185;">${p.blood_group}</span></td>
        <td>${p.phone}</td>
        <td><span class="badge badge-operational">Active Inpatient</span></td>
        <td>
          <button class="patient-action-btn" onclick="window.inspectPatient(${p.id})">Inspect Record 🔍</button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Patient list error", err);
  }
}

window.inspectPatient = async function(patientId) {
  try {
    const res = await fetch(`/api/v1/patients/${patientId}`, { headers: getHeaders() });
    if (res.status === 403) {
      const err = await res.json();
      showToast(`RBAC Restriction: ${err.detail}`, true);
      return;
    }
    if (!res.ok) {
      showToast("Unable to load patient profile.", true);
      return;
    }
    cachedPatient = await res.json();
    document.getElementById("modalPatientName").textContent = `${cachedPatient.first_name} ${cachedPatient.last_name}`;
    document.getElementById("modalPatientMrn").textContent = `${cachedPatient.mrn} | ID #${cachedPatient.id}`;
    document.getElementById("patientModal").classList.add("active");
    renderModalTab();
  } catch (err) {
    console.error("Inspect error", err);
    showToast("Error inspecting patient record", true);
  }
};

window.closePatientModal = function() {
  document.getElementById("patientModal").classList.remove("active");
  cachedPatient = null;
};

window.switchModalTab = function(tabName, el) {
  document.querySelectorAll(".modal-tab-btn").forEach(btn => btn.classList.remove("active"));
  if (el) el.classList.add("active");
  currentModalTab = tabName;
  renderModalTab();
};

function renderModalTab() {
  const body = document.getElementById("modalBody");
  if (!cachedPatient) return;
  const p = cachedPatient;

  if (currentModalTab === "demographics") {
    body.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
        <div class="card-panel">
          <h4 style="color: var(--accent-cyan); margin-bottom: 10px;">Primary Demographics</h4>
          <p><strong>Full Name:</strong> ${p.first_name} ${p.last_name}</p>
          <p><strong>MRN:</strong> <code>${p.mrn}</code></p>
          <p><strong>Date of Birth:</strong> ${p.dob}</p>
          <p><strong>Gender:</strong> ${p.gender}</p>
          <p><strong>Blood Group:</strong> ${p.blood_group}</p>
        </div>
        <div class="card-panel">
          <h4 style="color: var(--accent-cyan); margin-bottom: 10px;">Contact & Emergency</h4>
          <p><strong>Phone:</strong> ${p.phone}</p>
          <p><strong>Email:</strong> ${p.email}</p>
          <p><strong>Address:</strong> ${p.address}</p>
          <p><strong>Emergency Contact:</strong> ${p.emergency_contact || 'None listed'}</p>
        </div>
      </div>
    `;
  } else if (currentModalTab === "encounters") {
    body.innerHTML = `
      <h4 style="color: var(--accent-cyan); margin-bottom: 12px;">Encounter Timeline</h4>
      ${p.encounters.length === 0 ? '<p>No encounter history recorded.</p>' : p.encounters.map(e => `
        <div class="card-panel" style="margin-bottom: 10px;">
          <div style="display: flex; justify-content: space-between;">
            <strong>${e.encounter_number} (${e.encounter_type.toUpperCase()})</strong>
            <span class="badge badge-operational">${e.status}</span>
          </div>
          <p style="margin-top: 6px;"><strong>Chief Complaint:</strong> ${e.chief_complaint}</p>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Admitted: ${e.admission_date} | Triage Acuity Level: ${e.triage_acuity}</p>
        </div>
      `).join("")}
    `;
  } else if (currentModalTab === "clinical") {
    body.innerHTML = `
      <div style="margin-bottom: 16px;">
        <h4 style="color: var(--accent-amber); margin-bottom: 8px;">Active Conditions (ICD-10)</h4>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          ${p.conditions.map(c => `
            <span class="badge" style="background: rgba(59,130,246,0.15); color: #60a5fa; padding: 6px 12px; font-size: 12px;">
              <strong>${c.code}</strong> - ${c.name} (${c.clinical_status})
            </span>
          `).join("")}
        </div>
      </div>
      <div>
        <h4 style="color: var(--accent-emerald); margin-bottom: 8px;">Laboratory Reports (LOINC)</h4>
        ${p.lab_reports.map(l => `
          <div class="card-panel" style="margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between;">
              <strong>${l.test_name} (LOINC: ${l.test_code})</strong>
              <span class="badge ${l.interpretation === 'Normal' ? 'badge-operational' : 'badge-critical'}">${l.interpretation}</span>
            </div>
            <pre style="background: #060911; padding: 10px; border-radius: 4px; margin-top: 8px; font-family: var(--font-mono); font-size: 12px;">${JSON.stringify(l.result_data, null, 2)}</pre>
          </div>
        `).join("")}
      </div>
    `;
  } else if (currentModalTab === "radiology") {
    body.innerHTML = `
      <h4 style="color: var(--accent-cyan); margin-bottom: 12px;">Diagnostic Radiology Reports</h4>
      ${p.radiology_reports.map(r => `
        <div class="card-panel" style="margin-bottom: 10px;">
          <div style="display: flex; justify-content: space-between;">
            <strong>${r.modality} - ${r.study_name}</strong>
            <span class="badge badge-operational">${r.status}</span>
          </div>
          <p style="margin-top: 8px;"><strong>Findings:</strong> ${r.findings}</p>
          <p style="margin-top: 6px; color: var(--accent-cyan);"><strong>Impression:</strong> ${r.impression}</p>
        </div>
      `).join("")}
    `;
  } else if (currentModalTab === "consents") {
    body.innerHTML = `
      <h4 style="color: var(--accent-cyan); margin-bottom: 12px;">Patient Consent Authorizations</h4>
      ${p.consents.map(c => `
        <div class="dept-tile" style="margin-bottom: 10px;">
          <div style="display: flex; justify-content: space-between;">
            <strong>Type: ${c.consent_type}</strong>
            <span class="badge ${c.status === 'active' ? 'badge-operational' : 'badge-critical'}">${c.status}</span>
          </div>
          <p style="margin-top: 4px; font-size: 12px;">Scope: <code>${c.scope}</code> | Granted By: ${c.granted_by}</p>
        </div>
      `).join("")}
    `;
  } else if (currentModalTab === "fhir") {
    body.innerHTML = `
      <h4 style="color: var(--accent-cyan); margin-bottom: 10px;">HL7 FHIR R4 Compliant JSON Representation</h4>
      <div id="fhirJsonContainer" style="background: #060911; padding: 14px; border-radius: 6px; max-height: 400px; overflow-y: auto; font-family: var(--font-mono); font-size: 12px;">
        Loading FHIR payload...
      </div>
    `;
    fetch(`/api/v1/fhir/Patient/${p.id}`, { headers: getHeaders() })
      .then(res => res.json())
      .then(data => { document.getElementById("fhirJsonContainer").textContent = JSON.stringify(data, null, 2); })
      .catch(err => { document.getElementById("fhirJsonContainer").textContent = "Error fetching FHIR resource."; });
  }
}

// -------------------------------------------------------------
// STAFF, SCENARIOS & AUDIT LEDGER
// -------------------------------------------------------------
async function loadStaff() {
  try {
    const res = await fetch("/api/v1/staff", { headers: getHeaders() });
    if (!res.ok) return;
    const staff = await res.json();
    document.getElementById("staffTableBody").innerHTML = staff.map(s => `
      <tr>
        <td><code>${s.employee_id}</code></td>
        <td><strong>${s.first_name} ${s.last_name}</strong></td>
        <td>${s.role}</td>
        <td>${s.specialization || 'General Clinical'}</td>
        <td>${s.current_shift}</td>
        <td><span class="badge badge-operational">On-Duty</span></td>
      </tr>
    `).join("");
  } catch (err) { console.error("Staff error", err); }
}

async function loadInventory() {
  try {
    const res = await fetch("/api/v1/operations/inventory", { headers: getHeaders() });
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("bloodBankList").innerHTML = data.blood_units.map(b => `
      <div class="dept-tile" style="text-align: center;">
        <div style="font-size: 18px; font-weight: 700; color: var(--accent-rose);">${b.blood_group}</div>
        <div style="font-size: 13px; font-weight: 600;">${b.units_available} Units</div>
      </div>
    `).join("");

    document.getElementById("medicineStockList").innerHTML = data.medicines.map(m => `
      <div style="padding: 6px 0; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between;">
        <div><strong>${m.name}</strong> ${m.is_controlled_substance ? '<span class="badge badge-critical" style="font-size: 8px;">CTRL</span>' : ''}</div>
        <span style="font-family: var(--font-mono);">${m.stock_quantity} ${m.unit}</span>
      </div>
    `).join("");
  } catch (err) { console.error("Inventory error", err); }
}

async function loadScenarios() {
  try {
    const res = await fetch("/api/v1/simulation/scenarios", { headers: getHeaders() });
    if (!res.ok) return;
    const scenarios = await res.json();
    document.getElementById("scenariosContainer").innerHTML = scenarios.map(s => `
      <div class="scenario-card ${s.is_active ? 'active-scenario' : ''}">
        <div>
          <div class="scenario-header">
            <span class="scenario-title">${s.name}</span>
            <span class="badge ${s.severity_level === 'nominal' ? 'badge-operational' : (s.severity_level === 'critical' ? 'badge-critical' : 'badge-degraded')}">${s.severity_level}</span>
          </div>
          <p class="scenario-desc" style="margin-top: 8px;">${s.description}</p>
        </div>
        <button class="scenario-btn ${s.is_active ? 'active-btn' : ''}" onclick="window.triggerScenario('${s.scenario_code}')">
          ${s.is_active ? 'Active Scenario ✓' : 'Engage Scenario ⚡'}
        </button>
      </div>
    `).join("");
  } catch (err) { console.error("Scenarios error", err); }
}

window.triggerScenario = async function(scenarioCode) {
  try {
    const res = await fetch("/api/v1/simulation/scenarios/activate", {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ scenario_code: scenarioCode })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(`Activated ${data.scenario_code}: ${data.message}`);
      loadAllData();
    }
  } catch (err) { console.error(err); }
};

window.triggerEnvControl = async function(action) {
  try {
    const res = await fetch("/api/v1/simulation/controls", {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ action: action })
    });
    const data = await res.json();
    if (res.ok) { showToast(`Environment control applied: ${action}`); loadAllData(); }
  } catch (err) { console.error(err); }
};

window.toggleSubsystem = async function(code, status) {
  try {
    const res = await fetch(`/api/v1/system/subsystems/${code}`, {
      method: "PATCH",
      headers: getHeaders(),
      body: JSON.stringify({ status: status, details: `Manual toggle to ${status} via Command Centre.` })
    });
    if (res.ok) { showToast(`Subsystem ${code} transitioned to ${status}.`); loadOverview(); loadAuditEvents(); }
  } catch (err) { console.error(err); }
};

async function loadCanaries() {
  try {
    const res = await fetch("/api/v1/system/canaries", { headers: getHeaders() });
    if (!res.ok) return;
    const canaries = await res.json();
    document.getElementById("canaryTrapsList").innerHTML = canaries.map(c => `
      <div class="dept-tile" style="border-left: 3px solid ${c.is_tripped ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">
        <div style="display: flex; justify-content: space-between;">
          <strong>${c.secret_name}</strong>
          <span class="badge ${c.is_tripped ? 'badge-critical' : 'badge-operational'}">${c.is_tripped ? 'TRIPPED 🚨' : 'ARMED'}</span>
        </div>
        <p style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">Key: <code>${c.secret_key}</code></p>
        ${c.is_tripped ? `<p style="font-size: 11px; color: var(--accent-rose); margin-top: 2px;">Tripped By: ${c.last_tripped_by} (Count: ${c.tripped_count})</p>` : ''}
      </div>
    `).join("");
  } catch (err) { console.error("Canaries error", err); }
}

window.loadAuditEvents = async function() {
  try {
    const res = await fetch("/api/v1/audit/events?limit=50", { headers: getHeaders() });
    if (!res.ok) return;
    const events = await res.json();
    document.getElementById("auditStreamContainer").innerHTML = events.map(e => {
      const dClass = e.decision === 'PERMIT' ? 'audit-permit' : (e.decision === 'TRAPPED' ? 'audit-trapped' : 'audit-deny');
      return `
        <div class="audit-row">
          <span style="color: var(--text-muted);">${e.timestamp.substring(11, 19)}</span>
          <span class="${dClass}">[${e.decision}]</span>
          <span><strong>${e.actor_id}</strong> (${e.actor_role})</span>
          <span>${e.action} -> <code>${e.resource_type}${e.resource_id ? `/${e.resource_id}` : ''}</code></span>
          <span class="audit-hash">⛓️ ${e.entry_hash.substring(0, 12)}...</span>
        </div>
      `;
    }).join("");
  } catch (err) { console.error("Audit log error", err); }
};

window.verifyAuditLedger = async function() {
  try {
    const res = await fetch("/api/v1/audit/verify", { headers: getHeaders() });
    const data = await res.json();
    if (res.ok && data.status === "valid") {
      alert(`🛡️ AUDIT LEDGER CRYPTOGRAPHIC INTEGRITY VALID!\n\nTotal Records: ${data.total_records}\nLatest Merkle Root: ${data.last_hash}\n\nAll sequential SHA-256 blocks verified without tampering.`);
    } else {
      alert(`⚠️ AUDIT TAMPERING DETECTED!\n\n${JSON.stringify(data, null, 2)}`);
    }
  } catch (err) { console.error(err); }
};

// ==========================================
// PHASE 3: RESEARCH & DIGITAL TWIN HANDLERS
// ==========================================

window.loadExperimentComparison = async function() {
  try {
    const res = await fetch("/api/v1/research/experiments/comparison", { headers: getHeaders() });
    if (!res.ok) return;
    const data = await res.json();
    
    document.getElementById("matrixSummaryText").textContent = data.summary;
    const tbody = document.getElementById("experimentsMatrixBody");
    tbody.innerHTML = data.matrix.map(m => {
      const isBaseline = m.profile_code === "PROFILE_A";
      const isFullSec = m.profile_code === "PROFILE_D" || m.profile_code === "PROFILE_E";
      const badgeClass = isBaseline ? "badge-critical" : (isFullSec ? "badge-operational" : "badge-degraded");
      return `
        <tr>
          <td><strong>${m.profile_code}</strong></td>
          <td>${m.profile_name}</td>
          <td>${m.total_tests}</td>
          <td><span style="color: ${m.breached_tests > 0 ? 'var(--accent-rose)' : 'var(--accent-emerald)'}; font-weight: 600;">${m.breached_tests}</span></td>
          <td><span class="badge ${badgeClass}">${m.attack_success_rate_pct}%</span></td>
          <td>${m.unauthorized_access_count}</td>
          <td>${m.clinical_utility_pct}%</td>
          <td>${m.avg_decision_latency_ms} ms</td>
          <td>
            <button class="patient-action-btn" onclick="window.runProfileFromTable('${m.profile_code}')" style="padding: 4px 8px; font-size: 11px;">
              Re-run
            </button>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    console.error("Experiment comparison error", err);
  }
};

window.runProfileFromTable = function(profileCode) {
  document.getElementById("expProfileSelect").value = profileCode;
  window.runSelectedExperiment();
};

window.runSelectedExperiment = async function() {
  const profile = document.getElementById("expProfileSelect").value;
  const statusEl = document.getElementById("expRunStatus");
  const btn = document.getElementById("btnRunExperiment");

  btn.disabled = true;
  statusEl.textContent = `Executing benchmark for ${profile}... please wait.`;

  try {
    const res = await fetch(`/api/v1/research/experiments/run/${profile}`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({})
    });
    const result = await res.json();
    if (res.ok) {
      showToast(`Experiment completed! ${result.profile_name}: ASR ${result.attack_success_rate}%`);
      statusEl.textContent = `Completed ${result.experiment_id}: ASR ${result.attack_success_rate}%, Utility ${result.utility_score}%`;
      window.loadExperimentComparison();
      window.loadExecutedExperimentsList();
    } else {
      showToast(`Error running experiment: ${result.detail || 'Failed'}`, true);
      statusEl.textContent = "Execution failed.";
    }
  } catch (err) {
    console.error("Experiment run error", err);
    showToast("Error connecting to experiment runner", true);
    statusEl.textContent = "Execution error.";
  } finally {
    btn.disabled = false;
  }
};

window.loadBottleneckAnalysis = async function() {
  try {
    const res = await fetch("/api/v1/research/bottlenecks", { headers: getHeaders() });
    if (!res.ok) return;
    const b = await res.json();
    
    document.getElementById("bottleneckStressScore").textContent = `${b.overall_stress_score}/100`;
    document.getElementById("bottleneckSummary").textContent = `Hospital Status: ${b.stress_level} (${b.bottlenecks_detected_count} active bottlenecks identified)`;
    
    const container = document.getElementById("bottleneckListContainer");
    if (b.bottlenecks.length === 0) {
      container.innerHTML = '<div style="color: var(--accent-emerald); font-size: 12px;">✅ No systemic bottlenecks detected. Digital twin running nominally.</div>';
      return;
    }

    container.innerHTML = b.bottlenecks.map(item => `
      <div style="background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <strong style="color: var(--accent-amber); font-size: 12px;">${item.component}</strong>: ${item.detail}
        </div>
        <span class="badge ${item.severity === 'CRITICAL' ? 'badge-critical' : 'badge-degraded'}">${item.metric}</span>
      </div>
    `).join("");
  } catch (err) {
    console.error("Bottleneck error", err);
  }
};

window.runCounterfactualSimulation = async function() {
  const payload = {
    icu_capacity_delta: parseInt(document.getElementById("inputIcuDelta").value),
    ed_doctor_delta: parseInt(document.getElementById("inputDoctorDelta").value),
    patient_arrival_multiplier: parseFloat(document.getElementById("inputArrivalMult").value),
    lis_availability_pct: parseFloat(document.getElementById("inputLisAvail").value),
    simulation_duration_hours: 24
  };

  const container = document.getElementById("cfResultsContainer");
  container.innerHTML = '<div style="color: var(--accent-cyan); font-size: 12px; padding: 15px;">Simulating digital twin dynamics under parameter shifts...</div>';

  try {
    const res = await fetch("/api/v1/research/counterfactual/simulate", {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) {
      container.innerHTML = `<div style="color: var(--accent-rose); font-size: 12px;">Simulation error: ${data.detail}</div>`;
      return;
    }

    const proj = data.counterfactual_projections;
    const base = data.baseline;
    const divRiskPct = Math.round(proj.projected_diversion_risk * 100);

    container.innerHTML = `
      <div style="background: rgba(255,255,255,0.02); padding: 15px; border-radius: 6px; border-left: 3px solid var(--accent-cyan);">
        <div style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);">ID: ${data.simulation_id}</div>
        <div style="font-size: 13px; color: var(--text-primary); margin-top: 6px; line-height: 1.5;">${data.summary}</div>
      </div>

      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px;">
        <div class="kpi-card" style="padding: 10px;">
          <div style="font-size: 11px; color: var(--text-muted);">ICU Occupancy</div>
          <div style="font-size: 18px; font-weight: 700; color: ${proj.projected_icu_occupancy_pct >= 90 ? 'var(--accent-rose)' : 'var(--accent-cyan)'};">
            ${proj.projected_icu_occupancy_pct}%
          </div>
          <div style="font-size: 10px; color: var(--text-muted);">Baseline: ${base.icu_occupancy_pct}%</div>
        </div>

        <div class="kpi-card" style="padding: 10px;">
          <div style="font-size: 11px; color: var(--text-muted);">ED Wait Time</div>
          <div style="font-size: 18px; font-weight: 700; color: ${proj.projected_ed_wait_minutes >= 45 ? 'var(--accent-amber)' : 'var(--accent-emerald)'};">
            ${proj.projected_ed_wait_minutes} min
          </div>
          <div style="font-size: 10px; color: var(--text-muted);">Baseline: ${base.ed_wait_minutes} min</div>
        </div>

        <div class="kpi-card" style="padding: 10px;">
          <div style="font-size: 11px; color: var(--text-muted);">Diversion Risk</div>
          <div style="font-size: 18px; font-weight: 700; color: ${divRiskPct >= 50 ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">
            ${divRiskPct}%
          </div>
          <div style="font-size: 10px; color: var(--text-muted);">Resilience: +${proj.resilience_delta_score}</div>
        </div>
      </div>
    `;
    showToast("Counterfactual simulation projection evaluated.");
  } catch (err) {
    console.error("Counterfactual error", err);
  }
};

window.updateDifficultyLabel = function(val) {
  const labels = [
    "Level 0: Normal Operations",
    "Level 1: Single Operational Anomaly",
    "Level 2: Single Adversarial Event",
    "Level 3: Interacting Anomalies",
    "Level 4: Infrastructure Degradation + Adversary",
    "Level 5: Compound Adaptive Adversarial Scenario"
  ];
  document.getElementById("intelDiffVal").textContent = labels[val] || `Level ${val}`;
};

window.generateIntelligentScenario = async function() {
  const level = parseInt(document.getElementById("intelDiffSlider").value);
  const seedVal = document.getElementById("intelSeedInput").value;
  const seed = seedVal ? parseInt(seedVal) : null;

  const viewer = document.getElementById("intelScenarioViewer");
  viewer.innerHTML = '<span style="color: var(--accent-cyan);">Synthesizing scenario space (H × A × I × T × C)...</span>';

  try {
    const res = await fetch("/api/v1/research/intelligence/generate", {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ difficulty_level: level, seed: seed })
    });
    const scen = await res.json();
    if (!res.ok) {
      viewer.innerHTML = `<span style="color: var(--accent-rose);">Generation error: ${scen.detail}</span>`;
      return;
    }

    viewer.innerHTML = `
      <div style="color: var(--accent-cyan); font-weight: 700; font-size: 13px; margin-bottom: 8px;">
        ${scen.title} (Level ${scen.difficulty_level})
      </div>
      <div style="color: var(--text-secondary); margin-bottom: 12px; font-family: var(--font-sans); font-size: 12px;">
        ${scen.description}
      </div>
      <div style="margin-bottom: 10px;">
        <span style="color: var(--accent-amber);">Seed:</span> ${scen.seed} | 
        <span style="color: var(--accent-amber);">Threat:</span> ${scen.dimensions.threat_condition} | 
        <span style="color: var(--accent-amber);">Hospital State:</span> ${scen.dimensions.hospital_state}
      </div>
      <div style="color: var(--accent-purple); font-weight: 600; margin-bottom: 4px;">User Prompt:</div>
      <div style="background: rgba(255,255,255,0.04); padding: 8px; border-radius: 4px; margin-bottom: 8px; color: #fff;">
        ${scen.test_case.user_prompt}
      </div>
      <div style="color: var(--accent-emerald); font-weight: 600; margin-bottom: 4px;">Expected Security Invariant:</div>
      <div style="color: var(--text-muted); font-size: 11px;">
        ${scen.test_case.expected_security_behaviour}
      </div>
    `;
    showToast(`Scenario synthesized: Level ${scen.difficulty_level}`);
  } catch (err) {
    console.error("Scenario generation error", err);
  }
};

window.loadExecutedExperimentsList = async function() {
  try {
    const res = await fetch("/api/v1/research/experiments?limit=20", { headers: getHeaders() });
    if (!res.ok) return;
    const list = await res.json();
    const select = document.getElementById("reportExpSelect");
    if (list.length === 0) {
      select.innerHTML = '<option value="LATEST">Default Benchmark (Full Gateway)</option>';
      return;
    }
    select.innerHTML = list.map(item => `
      <option value="${item.experiment_id}">
        ${item.experiment_id} — ${item.profile_name} (ASR: ${item.attack_success_rate}%)
      </option>
    `).join("");
  } catch (err) {
    console.error("Load experiments error", err);
  }
};

window.downloadReport = function(format) {
  const expId = document.getElementById("reportExpSelect").value || "LATEST";
  window.open(`/api/v1/research/reports/${expId}?format=${format}`, "_blank");
};

window.runAdaptiveCampaignUI = async function() {
  const timeline = document.getElementById("adaptiveCampaignTimeline");
  timeline.innerHTML = '<span style="color: var(--accent-red); font-size: 12px;">Launching AAVA 4-Round Escalating Campaign... evaluating defenses...</span>';

  try {
    const res = await fetch("/api/v1/research/aava/adaptive-campaign", {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ target_patient_id: 1, total_rounds: 4 })
    });
    const data = await res.json();
    if (!res.ok) {
      timeline.innerHTML = `<span style="color: var(--accent-rose); font-size: 12px;">Campaign failed: ${data.detail}</span>`;
      return;
    }

    timeline.innerHTML = `
      <div style="padding: 10px; background: rgba(255,255,255,0.02); border-radius: 6px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <strong style="color: var(--accent-cyan); font-size: 13px;">Campaign ${data.campaign_id}</strong>
          <div style="font-size: 11px; color: var(--text-muted);">${data.total_rounds_executed} Rounds Executed | Verdict: ${data.resilience_verdict}</div>
        </div>
        <span class="badge ${data.campaign_asr_percentage === 0 ? 'badge-operational' : 'badge-critical'}" style="font-size: 13px;">
          Campaign ASR: ${data.campaign_asr_percentage}%
        </span>
      </div>
      <div style="display: grid; gap: 6px;">
        ${data.rounds_history.map(r => `
          <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; border-left: 3px solid ${r.attack_succeeded ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">
            <div>
              <div style="font-weight: 600; font-size: 12px; color: #fff;">${r.vector_name}</div>
              <div style="font-size: 11px; color: var(--text-secondary);">${r.strategy}</div>
            </div>
            <span class="badge ${r.attack_succeeded ? 'badge-critical' : 'badge-operational'}">
              ${r.status}
            </span>
          </div>
        `).join("")}
      </div>
    `;
    showToast(`AAVA Adaptive Campaign concluded (ASR: ${data.campaign_asr_percentage}%)`);
    loadAuditEvents();
  } catch (err) {
    console.error("Adaptive campaign error", err);
  }
};

// Initial boot
document.addEventListener("DOMContentLoaded", () => {
  loadAllData();
  setInterval(loadOverview, 12000);
});
