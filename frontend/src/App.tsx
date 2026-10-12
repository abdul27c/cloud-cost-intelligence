

import { useEffect, useMemo, useState } from "react";
import {
  getOverview,
  getInvestigations,
  refreshAnalysis,
  type AnalysisReport,
  type InvestigationReport,
  type CandidateChange,
} from "./api";
import "./App.css";

type NavItem =
  | "Overview"
  | "Cost analysis"
  | "Investigations"
  | "Recommendations";

const serviceColors = ["#8b9cfb", "#56c8b5", "#f1bd73", "#c2a0f8"];

function money(value: number) {
  return value.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
}

function App() {
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [investigations, setInvestigations] =
    useState<InvestigationReport | null>(null);
  const [activeNav, setActiveNav] = useState<NavItem>("Overview");
  const [selectedChange, setSelectedChange] = useState("");
  const [period, setPeriod] = useState("30 days");
  const [showAllChanges, setShowAllChanges] = useState(false);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function loadData() {
    setError("");
    setLoading(true);

    try {
      const [overview, investigationData] = await Promise.all([
        getOverview(),
        getInvestigations(),
      ]);

      setReport(overview);
      setInvestigations(investigationData);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not load the analytics reports.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function handleRefresh() {
    setRefreshing(true);
    setError("");

    try {
      const result = await refreshAnalysis();
      setReport(result.overview);
      setInvestigations(result.investigations);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not refresh the analytics.",
      );
    } finally {
      setRefreshing(false);
    }
  }

  const services = useMemo(
    () =>
      Object.entries(report?.spend_by_service_usd ?? {})
        .map(([name, amount], index) => ({
          name,
          amount,
          color: serviceColors[index % serviceColors.length],
        }))
        .sort((a, b) => b.amount - a.amount),
    [report],
  );

  const dailyEntries = useMemo(() => {
    const entries = Object.entries(report?.daily_spend_usd ?? {})
      .map(([date, amount]) => ({ date, amount }))
      .sort((a, b) => a.date.localeCompare(b.date));

    const days = Number.parseInt(period, 10);
    return entries.slice(-days);
  }, [report, period]);

  const chart = useMemo(() => {
    const values = dailyEntries.map((item) => item.amount);
    const min = Math.min(...values, 0);
    const max = Math.max(...values, 1);
    const range = max - min || 1;

    const points = values.map((value, index) => ({
      x: values.length <= 1 ? 300 : (index / (values.length - 1)) * 600,
      y: 165 - ((value - min) / range) * 145,
    }));

    const line = points
      .map((point, index) =>
        `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`,
      )
      .join(" ");

    return {
      line,
      area: points.length
        ? `${line} L 600 180 L 0 180 Z`
        : "",
      max,
    };
  }, [dailyEntries]);

  const anomalyCount = report?.anomalies.length ?? 0;
  const validRecords = report?.summary.valid_records ?? 0;
  const rejectedRecords = report?.summary.rejected_records ?? 0;
  const totalRecords = validRecords + rejectedRecords;
  const qualityPercent =
    totalRecords > 0 ? (validRecords / totalRecords) * 100 : 0;



 
  function navigate(item: NavItem) {
    setActiveNav(item);

    const sectionIds: Record<NavItem, string> = {
      Overview: "overview",
      "Cost analysis": "cost-analysis",
      Investigations: "investigations",
      Recommendations: "recommendations",
    };

    document.getElementById(sectionIds[item])?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  if (loading) {
    return (
      <main className="loading-screen">
        <div className="brand-mark">c<span>.</span></div>
        <h2>Loading Cloud Intelligence</h2>
        <p>Connecting to your Python analytics engine…</p>
      </main>
    );
  }

  if (error && !report) {
    return (
      <main className="loading-screen">
        <div className="brand-mark">c<span>.</span></div>
        <h2>Could not connect to the API</h2>
        <p>{error}</p>
        <p>
          Start FastAPI in your project terminal with:
        </p>
        <code>python -m uvicorn src.api:app --reload --port 8000</code>
        <button className="refresh-button" onClick={() => void loadData()}>
          Try again
        </button>
      </main>
    );
  }

  if (!report) return null;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          className="brand"
          href="#overview"
          onClick={() => setActiveNav("Overview")}
        >
          <span className="brand-mark">c<span>.</span></span>
          <span>
            <strong>cloudscope</strong>
            <small>COST INTELLIGENCE</small>
          </span>
        </a>

        <div className="workspace-label">WORKSPACE</div>

        <div className="workspace">
          <div className="workspace-avatar">D</div>
          <div>
            <strong>Demo environment</strong>
            <small>Sample cloud account</small>
          </div>
          <span className="workspace-dots">•••</span>
        </div>

        <div className="nav-label">ANALYTICS</div>

        <nav className="navigation">
          {([
            ["Overview", "◫"],
            ["Cost analysis", "▥"],
            ["Investigations", "⌕"],
            ["Recommendations", "↗"],
          ] as [NavItem, string][]).map(([item, icon]) => (
            <button
              key={item}
              className={`nav-item ${activeNav === item ? "active" : ""}`}
              onClick={() => navigate(item)}
            >
              <span className="nav-icon">{icon}</span>
              {item}
              {item === "Investigations" && anomalyCount > 0 && (
                <span className="nav-count">{anomalyCount}</span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="environment-card">
            <span className="environment-dot" />
            <div>
              <strong>Prototype mode</strong>
              <small>Synthetic billing data</small>
            </div>
          </div>

          <div className="profile">
            <div className="profile-avatar">AM</div>
            <div>
              <strong>Cloud analyst</strong>
              <small>Local workspace</small>
            </div>
            <span className="workspace-dots">•••</span>
          </div>
        </div>
      </aside>

      <main className="main-content" id="overview">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{activeNav}</strong>
          </div>
          <div className="topbar-right">
            <span className="demo-badge"><span /> SYNTHETIC DATA</span>
            <div className="top-avatar">AM</div>
          </div>
        </header>

        <div className="page-content">
          {error && (
            <div className="disclaimer" role="alert">
              <span>!</span>
              <p>{error}</p>
            </div>
          )}

          <section className="page-heading">
            <div>
              <div className="eyebrow">CLOUD FINANCIAL OPERATIONS</div>
              <h1>Cost overview<span className="heading-period">.</span></h1>
              <p className="subtitle">
                Understand your cloud spend. Investigate anomalies. Find opportunities.
              </p>
            </div>

            <div className="heading-actions">
              <select
                aria-label="Chart reporting period"
                value={period}
                onChange={(event) => setPeriod(event.target.value)}
                className="period-select"
              >
                <option>30 days</option>
                <option>60 days</option>
                <option>90 days</option>
              </select>

              <button
                className="refresh-button"
                onClick={() => void handleRefresh()}
                disabled={refreshing}
              >
                {refreshing ? "↻ Running…" : "↻ Refresh"}
              </button>
            </div>
          </section>

          <section className="metrics-grid">
            <article className="metric-card">
              <div className="metric-top">
                <span>Total cloud spend</span>
                <span className="metric-symbol">$</span>
              </div>
              <div className="metric-value">
                {money(report.summary.total_spend_usd)}
              </div>
              <div className="metric-foot">
                <span className="neutral-dot" /> Entire analyzed period · USD
              </div>
              <div className="metric-spark spark-purple">
                <span /><span /><span /><span /><span /><span /><span /><span /><span />
              </div>
            </article>

            <article className="metric-card">
              <div className="metric-top">
                <span>Cost anomalies</span>
                <span className="metric-symbol warning-symbol">!</span>
              </div>
              <div className="metric-value">{anomalyCount}</div>
              <div className="metric-foot">
                <span className="warning-dot" /> Detected by current rules
              </div>
              <div className="metric-spark spark-orange">
                <span /><span /><span /><span /><span /><span /><span /><span /><span />
              </div>
            </article>

            <article className="metric-card">
              <div className="metric-top">
                <span>Resources analyzed</span>
                <span className="metric-symbol">◇</span>
              </div>
              <div className="metric-value">
                {report.summary.resources_analyzed}
              </div>
              <div className="metric-foot">
                <span className="neutral-dot" />
                {Object.keys(report.spend_by_service_usd).length} service categories
              </div>
              <div className="metric-spark spark-green">
                <span /><span /><span /><span /><span /><span /><span /><span /><span />
              </div>
            </article>

            <article className="metric-card">
              <div className="metric-top">
                <span>Data quality</span>
                <span className="metric-symbol success-symbol">✓</span>
              </div>
              <div className="metric-value">{qualityPercent.toFixed(1)}%</div>
              <div className="metric-foot">
                <span className="success-dot" />
                {validRecords} valid · {rejectedRecords} rejected
              </div>
              <div className="quality-track">
                <span style={{ width: `${qualityPercent}%` }} />
              </div>
            </article>
          </section>

          <section className="charts-grid" id="cost-analysis">
            <article className="panel spending-panel">
              <div className="panel-heading">
                <div>
                  <h2>Spend over time</h2>
                  <p>Daily cloud spending · analyzed billing data</p>
                </div>
                <span className="panel-menu">•••</span>
              </div>

              <div className="chart-legend">
                <span className="legend-dot purple-dot" /> Daily spend
                <span className="legend-period">{period}</span>
              </div>

              <div className="line-chart">
                <div className="chart-y-labels">
                  <span>{money(chart.max)}</span>
                  <span>{money(chart.max * 0.75)}</span>
                  <span>{money(chart.max * 0.5)}</span>
                  <span>{money(chart.max * 0.25)}</span>
                  <span>$0</span>
                </div>

                <div className="chart-area">
                  <div className="grid-lines">
                    <i /><i /><i /><i /><i />
                  </div>

                  <svg
                    viewBox="0 0 600 180"
                    preserveAspectRatio="none"
                    role="img"
                    aria-label="Daily cloud spending based on the analysis report"
                  >
                    <defs>
                      <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#8b82f6" stopOpacity=".22" />
                        <stop offset="100%" stopColor="#8b82f6" stopOpacity="0" />
                      </linearGradient>
                    </defs>
                    {chart.area && <path d={chart.area} fill="url(#chartFill)" />}
                    {chart.line && (
                      <path
                        d={chart.line}
                        fill="none"
                        stroke="#8b82f6"
                        strokeWidth="2.5"
                        vectorEffect="non-scaling-stroke"
                        strokeLinejoin="round"
                      />
                    )}
                  </svg>

                  <div className="chart-x-labels">
                    <span>{dailyEntries[0]?.date ?? "—"}</span>
                    <span>{dailyEntries[Math.floor(dailyEntries.length / 3)]?.date ?? "—"}</span>
                    <span>{dailyEntries[Math.floor((dailyEntries.length * 2) / 3)]?.date ?? "—"}</span>
                    <span>{dailyEntries[dailyEntries.length - 1]?.date ?? "—"}</span>
                  </div>
                </div>
              </div>

              <div className="chart-note">
                <span className="info-icon">i</span>
                Daily totals come from the Python analysis report. The period selector filters the chart only.
              </div>
            </article>

            <article className="panel service-panel">
              <div className="panel-heading">
                <div>
                  <h2>Spend by service</h2>
                  <p>Distribution across cloud services</p>
                </div>
                <span className="panel-menu">•••</span>
              </div>

              <div className="service-total">
                <strong>{money(report.summary.total_spend_usd)}</strong>
                <span>USD total</span>
              </div>

              <div className="service-bars">
                {services.map((service) => (
                  <div className="service-row" key={service.name}>
                    <div className="service-label">
                      <span
                        className="service-color"
                        style={{ background: service.color }}
                      />
                      <span>{service.name}</span>
                      <strong>{money(service.amount)}</strong>
                    </div>
                    <div className="service-track">
                      <span
                        style={{
                          width: `${services[0]?.amount ? (service.amount / services[0].amount) * 100 : 0}%`,
                          background: service.color,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </section>

          <section className="panel anomaly-panel" id="investigations">
            <div className="panel-heading">
              <div>
                <div className="section-kicker">
                  <span className="warning-dot" /> NEEDS ATTENTION
                </div>
                <h2>Cost anomaly investigation</h2>
                <p>Investigate spending spikes using correlated change-event evidence.</p>
              </div>
              <span className="severity-badge">
                {anomalyCount} anomal{anomalyCount === 1 ? "y" : "ies"} detected
              </span>
            </div>

            {report.anomalies.length === 0 ? (
              <p>No anomalies were detected by the current analysis rules.</p>
            ) : (
              report.anomalies.map((anomaly) => {
                const investigation = investigations?.investigations.find(
                  (item) =>
                    item.anomaly.resource_id === anomaly.resource_id &&
                    item.anomaly.date === anomaly.date,
                );

                return (
                  <div key={`${anomaly.resource_id}-${anomaly.date}`}>
                    <div className="anomaly-summary">
                      <div className="anomaly-icon">↗</div>
                      <div className="anomaly-main">
                        <strong>{anomaly.resource_id}</strong>
                        <span>{anomaly.date} · {anomaly.reason}</span>
                      </div>
                      <div className="anomaly-stat">
                        <small>Observed</small>
                        <strong>{money(anomaly.observed_daily_cost_usd)}</strong>
                      </div>
                      <div className="anomaly-stat">
                        <small>Baseline</small>
                        <strong>{money(anomaly.baseline_daily_cost_usd)}</strong>
                      </div>
                      <div className="anomaly-stat anomaly-increase">
                        <small>Increase</small>
                        <strong>+{anomaly.increase_percent.toFixed(1)}%</strong>
                      </div>
                    </div>

                    <div className="investigation-title">
                      <div>
                        <h3>Related change events</h3>
                        <p>Ranked by resource match and timing</p>
                      </div>
                      <span className="score-label">RELEVANCE SCORE</span>
                    </div>

                    {!investigation || investigation.candidate_changes.length === 0 ? (
                      <p>No eligible nearby change events were found.</p>
                    ) : (
                      <div className="change-list">
                        {(showAllChanges
                          ? investigation.candidate_changes
                          : investigation.candidate_changes.slice(0, 2)
                        ).map((change: CandidateChange) => (
                          <button
                            key={change.event_id}
                            className={`change-row ${selectedChange === change.event_id ? "selected" : ""}`}
                            onClick={() =>
                              setSelectedChange(
                                selectedChange === change.event_id
                                  ? ""
                                  : change.event_id,
                              )
                            }
                          >
                            <span className={`change-indicator ${change.relevance_score >= 60 ? "strong" : ""}`} />
                            <span className="change-content">
                              <span className="change-id">
                                {change.change_id}
                                <small>{change.event_time.replace("T", " ")}</small>
                              </span>
                              <span className="change-description">
                                <strong>{change.resource_id}</strong>
                                <small>{change.description}</small>
                              </span>
                              <span className={`change-score ${change.relevance_score >= 60 ? "high-score" : ""}`}>
                                {change.relevance_score}
                                <small>{change.assessment}</small>
                              </span>

                              {selectedChange === change.event_id && (
                                <span className="change-evidence">
                                  <strong>Evidence considered</strong>
                                  {change.evidence.map((evidence) => (
                                    <span key={evidence}>• {evidence}</span>
                                  ))}
                                  <em>
                                    {change.causation_confirmed
                                      ? "Causation was confirmed by the analysis."
                                      : "Correlation does not establish causation."}
                                  </em>
                                </span>
                              )}
                            </span>
                            <span className="change-chevron">
                              {selectedChange === change.event_id ? "−" : "+"}
                            </span>
                          </button>
                        ))}
                      </div>
                    )}

                    {investigation && investigation.candidate_changes.length > 2 && (
                      <button
                        className="text-button"
                        onClick={() => setShowAllChanges(!showAllChanges)}
                      >
                        {showAllChanges ? "Show fewer changes ↑" : "View all candidate changes →"}
                      </button>
                    )}

                    {investigation && (
                      <p className="chart-note">{investigation.conclusion}</p>
                    )}
                  </div>
                );
              })
            )}

            <div className="disclaimer">
              <span>ⓘ</span>
              <p>
                <strong>Investigative lead, not a confirmed cause.</strong>{" "}
                Resource and timing matches help prioritize review. Daily billing
                data cannot establish the exact order of events within the same day.
              </p>
            </div>
          </section>

          <section className="recommendations-grid" id="recommendations">
            <article className="panel recommendation-panel">
              <div className="panel-heading">
                <div>
                  <h2>Optimization opportunities</h2>
                  <p>Recommendations generated by the Python analysis</p>
                </div>
                <span className="panel-menu">•••</span>
              </div>

              {report.recommendations.length === 0 ? (
                <p>No recommendations were generated.</p>
              ) : (
                report.recommendations.map((item) => (
                  <div className="recommendation-item" key={item.resource_id}>
                    <span className="recommendation-icon">◷</span>
                    <div>
                      <strong>{item.resource_id}</strong>
                      <p>{item.recommendation}</p>
                      <p>{item.evidence}</p>
                      <span className="priority-label">
                        {item.priority.toUpperCase()} PRIORITY
                      </span>
                      {item.estimated_savings_usd != null && (
                        <p>Estimated savings: {money(item.estimated_savings_usd)}</p>
                      )}
                      {item.note && <p>{item.note}</p>}
                    </div>
                  </div>
                ))
              )}
            </article>

            <article className="panel quality-panel">
              <div className="panel-heading">
                <div>
                  <h2>Data integrity</h2>
                  <p>Input validation summary</p>
                </div>
              </div>

              <div className="integrity-value">
                {validRecords} <span>valid records</span>
              </div>
              <div className="integrity-bar">
                <span style={{ width: `${qualityPercent}%` }} />
              </div>
              <div className="integrity-line">
                <span>Accepted billing records</span>
                <strong>{qualityPercent.toFixed(1)}%</strong>
              </div>
              <div className="integrity-line">
                <span>Rejected billing records</span>
                <strong>{rejectedRecords}</strong>
              </div>
              <div className="integrity-line">
                <span>Days analyzed</span>
                <strong>{report.summary.days_analyzed}</strong>
              </div>
              <div className="integrity-line">
                <span>Change events loaded</span>
                <strong>{investigations?.events_loaded ?? "—"}</strong>
              </div>
              <p className="integrity-footnote">
                Invalid input is excluded from the analysis rather than silently
                included in totals.
              </p>
            </article>
          </section>

          <footer className="footer">
            <span>
              <span className="footer-dot" /> Cloudscope
              <span className="footer-divider">/</span> Cloud Cost Intelligence
            </span>
            <span>Portfolio prototype · Synthetic data · 2026</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;
