
import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowRight,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  Code2,
  Database,
  GitCompareArrows,
  LayoutDashboard,
  LoaderCircle,
  Play,
  RefreshCw,
  Search,
  Server,
  ShieldCheck,
  Wrench,
  XCircle,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { dashboardAPI } from "./services/api";
import "./App.css";

const NAVIGATION = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "differential", label: "Differential Analysis", icon: GitCompareArrows },
  { id: "ldi", label: "LDI Analysis", icon: Activity },
  { id: "localization", label: "Root-Cause Analysis", icon: Search },
  { id: "repair", label: "Repair Evaluation", icon: Wrench },
];

const money = (value) => {
  if (value === null || value === undefined) return "—";

  const number = Number(value);

  if (!Number.isFinite(number)) return String(value);

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
  }).format(number);
};

const decimal = (value, digits = 4) => {
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(digits) : "—";
};

function StatusPill({ good, children }) {
  return (
    <span className={`status-pill ${good ? "success" : "warning"}`}>
      {good ? <CheckCircle2 size={13} /> : <AlertTriangle size={13} />}
      {children}
    </span>
  );
}

function MetricCard({ label, value, subtitle, icon: Icon, accent }) {
  return (
    <div className={`metric-card ${accent || ""}`}>
      <div className="metric-top">
        <span>{label}</span>
        <span className="metric-icon">
          <Icon size={19} />
        </span>
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-subtitle">{subtitle}</div>
    </div>
  );
}

function SectionHeading({ eyebrow, title, description, action }) {
  return (
    <div className="section-heading">
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      {action}
    </div>
  );
}

function EmptyState({ title, description }) {
  return (
    <div className="empty-state">
      <Database size={30} />
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function ActionButton({
  children,
  icon: Icon = Play,
  onClick,
  loading,
  disabled,
  secondary = false,
}) {
  return (
    <button
      className={`action-button ${secondary ? "secondary" : ""}`}
      onClick={onClick}
      disabled={loading || disabled}
      type="button"
    >
      {loading ? (
        <LoaderCircle size={16} className="spin" />
      ) : (
        <Icon size={16} />
      )}
      {children}
    </button>
  );
}

function App() {
  const [activePage, setActivePage] = useState("overview");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [selectedCase, setSelectedCase] = useState(null);

  const loadDashboard = useCallback(async () => {
    setLoading(true);

    try {
      const result = await dashboardAPI.getDashboard();
      setData(result);
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const performAction = async (action, name) => {
    setRunning(name);
    setError("");
    setNotice("");

    try {
      await action();
      const result = await dashboardAPI.getDashboard();
      setData(result);
      setNotice(`${name} completed successfully.`);
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning("");
    }
  };

  const drift = data?.drift;
  const ldi = data?.ldi;
  const observations = data?.observations || [];
  const localization = data?.localization;
  const patch = data?.patch;
  const repair = data?.repair;

  const driftedIds = new Set(drift?.drifted_case_ids || []);

  const selectedObservation =
    observations.find((item) => item.test_id === selectedCase) ||
    observations.find((item) => driftedIds.has(item.test_id)) ||
    observations[0];

  const chartData = observations.map((item) => ({
    name: item.test_id,
    legacy: Number(item.legacy?.final_total) || 0,
    modernized: Number(item.modernized?.final_total) || 0,
  }));

  const currentPage =
    NAVIGATION.find((page) => page.id === activePage) ||
    NAVIGATION[0];

  const runAnalysisButton = (
    <ActionButton
      onClick={() =>
        performAction(dashboardAPI.runAnalysis, "Drift analysis")
      }
      loading={running === "Drift analysis"}
      disabled={Boolean(running)}
    >
      Run Drift Analysis
    </ActionButton>
  );

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <GitCompareArrows size={24} />
          </div>
          <div>
            <h1>DRIFTSCOPE</h1>
            <span>Migration Intelligence</span>
          </div>
        </div>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="navigation">
          {NAVIGATION.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              className={`nav-item ${
                activePage === id ? "active" : ""
              }`}
              onClick={() => setActivePage(id)}
            >
              <Icon size={18} />
              <span>{label}</span>
              {activePage === id && <ChevronRight size={15} />}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="environment-card">
            <div className="environment-heading">
              <CircleDot size={15} />
              EXPERIMENT ENVIRONMENT
            </div>
            <div className="environment-row">
              <span>Reference</span>
              <strong>Monolith</strong>
            </div>
            <div className="environment-row">
              <span>Target</span>
              <strong>Microservices</strong>
            </div>
            <div className="environment-row">
              <span>Mode</span>
              <strong>HTTP Comparison</strong>
            </div>
          </div>
          <div className="sidebar-caption">
            Business-Logic Drift Research Prototype
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <ChevronRight size={14} />
            <strong>{currentPage.label}</strong>
          </div>
          <div className="topbar-actions">
            <span className="api-status">
              <span className="online-dot" />
              {data ? "Analysis API connected" : "Waiting for API"}
            </span>
            <button
              type="button"
              className="icon-button"
              title="Refresh dashboard"
              onClick={loadDashboard}
              disabled={loading}
            >
              <RefreshCw
                size={17}
                className={loading ? "spin" : ""}
              />
            </button>
          </div>
        </header>

        <div className="page-content">
          {error && (
            <div className="alert error-alert">
              <XCircle size={18} />
              <span>{error}</span>
              <button onClick={() => setError("")}>Dismiss</button>
            </div>
          )}

          {notice && (
            <div className="alert success-alert">
              <CheckCircle2 size={18} />
              <span>{notice}</span>
              <button onClick={() => setNotice("")}>Dismiss</button>
            </div>
          )}

          {activePage === "overview" && (
            <>
              <SectionHeading
                eyebrow="EXPERIMENT OVERVIEW"
                title="Migration Drift Dashboard"
                description="Observe behavioral differences between the legacy monolith and modernized microservices."
                action={runAnalysisButton}
              />

              <div className="metrics-grid">
                <MetricCard
                  label="Test Cases"
                  value={drift?.total_test_cases ?? "—"}
                  subtitle="Executed checkout scenarios"
                  icon={Database}
                />
                <MetricCard
                  label="Drifted Cases"
                  value={drift?.drifted_test_cases ?? "—"}
                  subtitle="Behavioral mismatches"
                  icon={AlertTriangle}
                  accent="amber"
                />
                <MetricCard
                  label="Logic Drift Index"
                  value={decimal(ldi?.ldi_score)}
                  subtitle="Weighted divergence / 100"
                  icon={Activity}
                  accent="violet"
                />
                <MetricCard
                  label="Repair Status"
                  value={
                    repair
                      ? repair.repair_accepted
                        ? "Accepted"
                        : "Rejected"
                      : "Pending"
                  }
                  subtitle="Candidate validation"
                  icon={ShieldCheck}
                  accent="green"
                />
              </div>

              <div className="two-column">
                <section className="panel">
                  <div className="panel-header">
                    <div>
                      <h3>Checkout Output Comparison</h3>
                      <p>Final totals by test case</p>
                    </div>
                    <GitCompareArrows size={18} />
                  </div>

                  {chartData.length ? (
                    <div className="chart-container">
                      <ResponsiveContainer width="100%" height={290}>
                        <BarChart data={chartData}>
                          <CartesianGrid
                            stroke="#26334B"
                            vertical={false}
                          />
                          <XAxis
                            dataKey="name"
                            stroke="#8795AB"
                            fontSize={11}
                          />
                          <YAxis
                            stroke="#8795AB"
                            fontSize={11}
                          />
                          <Tooltip
                            contentStyle={{
                              background: "#162238",
                              border: "1px solid #334155",
                              borderRadius: 10,
                              color: "#E2E8F0",
                            }}
                          />
                          <Bar
                            dataKey="legacy"
                            name="Legacy"
                            fill="#6478F5"
                            radius={[4, 4, 0, 0]}
                          />
                          <Bar
                            dataKey="modernized"
                            name="Modernized"
                            fill="#32C5B1"
                            radius={[4, 4, 0, 0]}
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <EmptyState
                      title="No observations yet"
                      description="Run drift analysis to generate comparison data."
                    />
                  )}
                </section>

                <section className="panel">
                  <div className="panel-header">
                    <div>
                      <h3>Drift Summary</h3>
                      <p>Current experiment findings</p>
                    </div>
                    <AlertTriangle size={18} />
                  </div>

                  <div className="summary-list">
                    <div className="summary-item">
                      <span>Observed drift</span>
                      <StatusPill good={drift?.drifted_test_cases === 0}>
                        {drift
                          ? drift.drifted_test_cases === 0
                            ? "No drift"
                            : "Drift detected"
                          : "Not analyzed"}
                      </StatusPill>
                    </div>

                    <div className="summary-item">
                      <span>Affected cases</span>
                      <strong>
                        {drift?.drifted_case_ids?.join(", ") || "None"}
                      </strong>
                    </div>

                    <div className="summary-item">
                      <span>Baseline LDI</span>
                      <strong>{decimal(ldi?.ldi_score)}</strong>
                    </div>

                    <div className="summary-item">
                      <span>Candidate LDI</span>
                      <strong>
                        {decimal(repair?.candidate_ldi)}
                      </strong>
                    </div>

                    <div className="summary-item">
                      <span>Critical rule</span>
                      <strong>
                        {repair
                          ? repair.critical_rule_passed
                            ? "Passed"
                            : "Failed"
                          : "Not evaluated"}
                      </strong>
                    </div>
                  </div>

                  <button
                    className="text-link"
                    onClick={() => setActivePage("differential")}
                  >
                    Explore differences <ArrowRight size={15} />
                  </button>
                </section>
              </div>

              <section className="panel">
                <div className="panel-header">
                  <div>
                    <h3>Analysis Pipeline</h3>
                    <p>End-to-end workflow</p>
                  </div>
                </div>

                <div className="pipeline">
                  {[
                    ["01", "Record", "Capture API responses"],
                    ["02", "Compare", "Identify divergences"],
                    ["03", "Quantify", "Calculate LDI"],
                    ["04", "Localize", "Identify candidate cause"],
                    ["05", "Repair", "Validate candidate"],
                  ].map(([number, title, detail], index) => (
                    <div className="pipeline-step" key={number}>
                      <span className="step-number">{number}</span>
                      <strong>{title}</strong>
                      <small>{detail}</small>
                      {index < 4 && (
                        <ArrowRight size={16} className="step-arrow" />
                      )}
                    </div>
                  ))}
                </div>
              </section>
            </>
          )}

          {activePage === "differential" && (
            <>
              <SectionHeading
                eyebrow="BEHAVIOR COMPARISON"
                title="Differential Analysis"
                description="Inspect the responses produced by both implementations for identical checkout requests."
                action={runAnalysisButton}
              />

              <section className="panel">
                <div className="panel-header">
                  <h3>Test Case Results</h3>
                  <span className="muted">
                    {observations.length} observations
                  </span>
                </div>

                {observations.length ? (
                  <div className="table-scroll">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Test ID</th>
                          <th>Legacy Total</th>
                          <th>Modernized Total</th>
                          <th>Result</th>
                          <th></th>
                        </tr>
                      </thead>
                      <tbody>
                        {observations.map((item) => {
                          const hasDrift = driftedIds.has(item.test_id);

                          return (
                            <tr key={item.test_id}>
                              <td className="mono">{item.test_id}</td>
                              <td>{money(item.legacy?.final_total)}</td>
                              <td>{money(item.modernized?.final_total)}</td>
                              <td>
                                <StatusPill good={!hasDrift}>
                                  {hasDrift ? "Drift" : "Match"}
                                </StatusPill>
                              </td>
                              <td>
                                <button
                                  className="table-action"
                                  onClick={() =>
                                    setSelectedCase(item.test_id)
                                  }
                                >
                                  Inspect <ChevronRight size={14} />
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <EmptyState
                    title="No test results"
                    description="Run analysis to populate this table."
                  />
                )}
              </section>

              {selectedObservation && (
                <section className="panel">
                  <div className="panel-header">
                    <div>
                      <h3>
                        {selectedObservation.test_id} — Field Comparison
                      </h3>
                      <p>{selectedObservation.description}</p>
                    </div>
                  </div>

                  <div className="comparison-grid">
                    {[
                      "status",
                      "subtotal",
                      "discount",
                      "tax",
                      "final_total",
                      "business_decision",
                      "order_created",
                    ].map((field) => {
                      const legacyValue =
                        selectedObservation.legacy?.[field];
                      const modernValue =
                        selectedObservation.modernized?.[field];
                      const different =
                        String(legacyValue) !== String(modernValue);

                      return (
                        <div
                          className={`comparison-row ${
                            different ? "different" : ""
                          }`}
                          key={field}
                        >
                          <span>{field.replaceAll("_", " ")}</span>
                          <strong>{String(legacyValue ?? "—")}</strong>
                          <strong>{String(modernValue ?? "—")}</strong>
                        </div>
                      );
                    })}
                    <div className="comparison-labels">
                      <span>Field</span>
                      <span>Legacy</span>
                      <span>Modernized</span>
                    </div>
                  </div>
                </section>
              )}
            </>
          )}

          {activePage === "ldi" && (
            <>
              <SectionHeading
                eyebrow="DRIFT QUANTIFICATION"
                title="Logic Drift Index"
                description="A weighted measurement of observed differences across the checkout test suite."
                action={runAnalysisButton}
              />

              <div className="metrics-grid two-metrics">
                <MetricCard
                  label="Baseline LDI"
                  value={decimal(ldi?.ldi_score)}
                  subtitle="Current modernized implementation"
                  icon={Activity}
                />
                <MetricCard
                  label="Repaired LDI"
                  value={decimal(repair?.candidate_ldi)}
                  subtitle="Candidate implementation"
                  icon={ArrowDownRight}
                  accent="green"
                />
              </div>

              <section className="panel">
                <div className="panel-header">
                  <div>
                    <h3>Per-Test Output Comparison</h3>
                    <p>Checkout final totals in INR</p>
                  </div>
                </div>

                {chartData.length ? (
                  <div className="chart-container large">
                    <ResponsiveContainer width="100%" height={340}>
                      <BarChart data={chartData}>
                        <CartesianGrid
                          stroke="#26334B"
                          vertical={false}
                        />
                        <XAxis
                          dataKey="name"
                          stroke="#8795AB"
                        />
                        <YAxis stroke="#8795AB" />
                        <Tooltip
                          contentStyle={{
                            background: "#162238",
                            border: "1px solid #334155",
                            borderRadius: 10,
                          }}
                        />
                        <Bar
                          dataKey="legacy"
                          fill="#6478F5"
                          name="Legacy"
                        />
                        <Bar
                          dataKey="modernized"
                          fill="#32C5B1"
                          name="Modernized"
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <EmptyState
                    title="No LDI data"
                    description="Run drift analysis to calculate LDI."
                  />
                )}
              </section>

              <div className="info-panel">
                <Code2 size={20} />
                <div>
                  <strong>Interpreting the LDI</strong>
                  <p>
                    A score of zero indicates no measured drift in the
                    evaluated test cases. A low aggregate score does not
                    guarantee that critical business rules are preserved.
                    The repair evaluator checks the discount boundary
                    separately.
                  </p>
                </div>
              </div>
            </>
          )}

          {activePage === "localization" && (
            <>
              <SectionHeading
                eyebrow="ROOT-CAUSE INVESTIGATION"
                title="Root-Cause Analysis"
                description="Map observed field mismatches to services and inspect known defect patterns."
                action={
                  <ActionButton
                    icon={Search}
                    onClick={() =>
                      performAction(
                        dashboardAPI.localize,
                        "Root-cause localization"
                      )
                    }
                    loading={running === "Root-cause localization"}
                    disabled={Boolean(running)}
                  >
                    Localize Root Cause
                  </ActionButton>
                }
              />

              <div className="metrics-grid two-metrics">
                <MetricCard
                  label="Suspected Service"
                  value={
                    localization?.suspected_root_cause ||
                    "Not identified"
                  }
                  subtitle="Pattern-based localization"
                  icon={Server}
                  accent="violet"
                />
                <MetricCard
                  label="Known Defect Pattern"
                  value={
                    localization
                      ? localization.known_defect_found
                        ? "Detected"
                        : "Not detected"
                      : "Pending"
                  }
                  subtitle="Source inspection result"
                  icon={Search}
                />
              </div>

              <section className="panel">
                <div className="panel-header">
                  <h3>Localization Findings</h3>
                </div>

                {localization?.findings?.length ? (
                  <div className="table-scroll">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Test</th>
                          <th>Field</th>
                          <th>Suspected Component</th>
                          <th>Legacy</th>
                          <th>Modernized</th>
                        </tr>
                      </thead>
                      <tbody>
                        {localization.findings.map((item, index) => (
                          <tr key={`${item.test_id}-${item.field}-${index}`}>
                            <td>{item.test_id}</td>
                            <td>{item.field}</td>
                            <td className="mono">
                              {item.suspected_service}
                            </td>
                            <td>{String(item.legacy_value)}</td>
                            <td>{String(item.modernized_value)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <EmptyState
                    title="No localization report"
                    description="Run root-cause localization to inspect drift findings."
                  />
                )}
              </section>

              {localization?.known_defect_found && (
                <section className="panel">
                  <div className="panel-header">
                    <h3>Identified Repair Pattern</h3>
                    <StatusPill good={false}>
                      Boundary condition mismatch
                    </StatusPill>
                  </div>

                  <div className="code-comparison">
                    <div>
                      <span>Original condition</span>
                      <code>{localization.faulty_expression}</code>
                    </div>
                    <ArrowRight size={20} />
                    <div>
                      <span>Proposed correction</span>
                      <code>{localization.proposed_expression}</code>
                    </div>
                  </div>
                </section>
              )}
            </>
          )}

          {activePage === "repair" && (
            <>
              <SectionHeading
                eyebrow="CONTROLLED REPAIR VALIDATION"
                title="Repair Evaluation"
                description="Generate a candidate patch and compare its observed behavior against the legacy reference."
                action={
                  <ActionButton
                    icon={Wrench}
                    onClick={() =>
                      performAction(
                        dashboardAPI.repair,
                        "Repair evaluation"
                      )
                    }
                    loading={running === "Repair evaluation"}
                    disabled={Boolean(running)}
                  >
                    Generate & Evaluate Repair
                  </ActionButton>
                }
              />

              <div className="metrics-grid">
                <MetricCard
                  label="Before Repair"
                  value={decimal(repair?.baseline_ldi)}
                  subtitle="Baseline LDI"
                  icon={Activity}
                />
                <MetricCard
                  label="After Repair"
                  value={decimal(repair?.candidate_ldi)}
                  subtitle="Candidate LDI"
                  icon={ArrowDownRight}
                  accent="green"
                />
                <MetricCard
                  label="LDI Reduction"
                  value={decimal(repair?.ldi_reduction)}
                  subtitle="Absolute score reduction"
                  icon={GitCompareArrows}
                />
                <MetricCard
                  label="Decision"
                  value={
                    repair
                      ? repair.repair_accepted
                        ? "Accepted"
                        : "Rejected"
                      : "Pending"
                  }
                  subtitle="Automated acceptance gate"
                  icon={ShieldCheck}
                  accent="green"
                />
              </div>

              <div className="two-column">
                <section className="panel">
                  <div className="panel-header">
                    <h3>Validation Checks</h3>
                  </div>

                  {repair ? (
                    <div className="summary-list">
                      {[
                        ["Baseline verified", repair.baseline_valid],
                        [
                          "Critical business rule",
                          repair.critical_rule_passed,
                        ],
                        [
                          "No observed regressions",
                          repair.no_observed_regressions,
                        ],
                        [
                          "Candidate accepted",
                          repair.repair_accepted,
                        ],
                      ].map(([label, passed]) => (
                        <div className="summary-item" key={label}>
                          <span>{label}</span>
                          <StatusPill good={passed}>
                            {passed ? "Passed" : "Failed"}
                          </StatusPill>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <EmptyState
                      title="No repair evaluation"
                      description="Run candidate repair evaluation first."
                    />
                  )}
                </section>

                <section className="panel">
                  <div className="panel-header">
                    <h3>Generated Patch</h3>
                  </div>

                  {patch ? (
                    <div className="patch-details">
                      <div className="patch-line removed">
                        - {patch.original_expression}
                      </div>
                      <div className="patch-line added">
                        + {patch.repaired_expression}
                      </div>
                      <div className="patch-meta">
                        <span>Strategy</span>
                        <strong>{patch.repair_strategy}</strong>
                      </div>
                      <div className="patch-meta">
                        <span>Original preserved</span>
                        <strong>
                          {patch.original_modified === false
                            ? "Yes"
                            : "No"}
                        </strong>
                      </div>
                    </div>
                  ) : (
                    <EmptyState
                      title="No generated patch"
                      description="Generate a candidate repair to inspect the proposed change."
                    />
                  )}
                </section>
              </div>

              {repair && (
                <div className="info-panel">
                  <ShieldCheck size={20} />
                  <div>
                    <strong>Evaluation scope</strong>
                    <p>
                      {repair.evaluation_scope}. Acceptance indicates
                      that the candidate passed the defined checks,
                      not that every possible input or production
                      scenario has been verified.
                    </p>
                  </div>
                </div>
              )}
            </>
          )}

          <footer className="footer">
            <span>DRIFTSCOPE · Academic Research Prototype</span>
            <span>Monolith → Microservices · Logic Drift Analysis</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;
