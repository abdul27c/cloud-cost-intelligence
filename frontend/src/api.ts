
const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export interface CostAnomaly {
  resource_id: string;
  date: string;
  baseline_daily_cost_usd: number;
  observed_daily_cost_usd: number;
  increase_usd: number;
  increase_percent: number;
  reason: string;
}

export interface Recommendation {
  resource_id: string;
  priority: string;
  recommendation: string;
  evidence: string;
  estimated_savings_usd: number | null;
  note: string;
}

export interface AnalysisReport {
  summary: {
    valid_records: number;
    rejected_records: number;
    total_spend_usd: number;
    resources_analyzed: number;
    days_analyzed: number;
  };
  spend_by_service_usd: Record<string, number>;
  daily_spend_usd: Record<string, number>;
  anomalies: CostAnomaly[];
  recommendations: Recommendation[];
  rejected_rows: unknown[];
}

export interface CandidateChange {
  event_id: string;
  change_id: string;
  event_time: string;
  resource_id: string;
  event_type: string;
  description: string;
  days_from_anomaly: number;
  same_resource: boolean;
  relevance_score: number;
  assessment: string;
  evidence: string[];
  causation_confirmed: boolean;
}

export interface Investigation {
  anomaly: CostAnomaly;
  candidate_changes: CandidateChange[];
  conclusion: string;
}

export interface InvestigationReport {
  anomalies_investigated: number;
  events_loaded: number;
  investigations: Investigation[];
  rejected_events: unknown[];
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);

  if (!response.ok) {
    throw new Error(`API request failed (${response.status}): ${path}`);
  }

  return response.json() as Promise<T>;
}

export function getOverview(): Promise<AnalysisReport> {
  return request<AnalysisReport>("/api/overview");
}

export function getInvestigations(): Promise<InvestigationReport> {
  return request<InvestigationReport>("/api/investigations");
}

export async function refreshAnalysis(): Promise<{
  overview: AnalysisReport;
  investigations: InvestigationReport;
}> {
  const response = await fetch(`${API_URL}/api/refresh`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(`Refresh failed (${response.status})`);
  }

  return response.json();
}
