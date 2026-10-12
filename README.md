# Cloud Cost Intelligence & Optimization Platform

A cloud cost analysis prototype that identifies unusual spending patterns, highlights potential optimization opportunities, and correlates cost anomalies with recent infrastructure changes.

The project combines a Python analytics engine, a FastAPI backend, and a custom React dashboard to demonstrate how cloud cost data can be transformed into actionable investigation insights.

> **Project status:** Local prototype using synthetic billing data and simulated infrastructure change events. Live AWS billing integration and cloud deployment are planned future improvements.

## Features

- **Cost analysis:** Calculate total spending, daily spending trends, and spending by service.
- **Anomaly detection:** Identify unusually high daily costs relative to a recent historical baseline.
- **Optimization recommendations:** Flag development resources that may benefit from scheduled shutdowns.
- **Change-event correlation:** Rank recent infrastructure changes by their potential relevance to a cost anomaly.
- **Data validation:** Reject malformed billing records and non-finite cost values.
- **Interactive dashboard:** Explore spending metrics, anomalies, investigation evidence, and recommendations.
- **Automated tests:** Validate core analysis and correlation behavior with pytest.

## Technology Stack

| Component | Technology |
|---|---|
| Analytics engine | Python |
| Data processing | pandas |
| API | FastAPI |
| API server | Uvicorn |
| Frontend | React, TypeScript, Vite |
| Original dashboard | Streamlit |
| Testing | pytest |

## Architecture

```text
Synthetic Billing Data
          |
          v
   Python Analyzer
          |
          +----> Cost Summary
          +----> Daily Spending
          +----> Anomaly Detection
          +----> Recommendations
          |
          v
   Analysis JSON Report
          |
          +-----------------------+
          |                       |
          v                       v
   FastAPI Backend        Change Correlator
          |                       ^
          |                 Change Events
          v                       |
   React + TypeScript <--- Investigation JSON
          |
          v
   Interactive Dashboard
```

The analyzer and change correlator generate JSON reports that the API serves to the frontend. The dashboard displays those results without requiring the analytics logic to run in the browser.

## How Anomaly Detection Works

The analyzer compares daily resource spending with a recent historical baseline.

The current prototype flags a potential anomaly when both conditions are met:

1. Daily spending is at least three times the recent median.
2. Daily spending exceeds that baseline by at least $10.

Detected anomalies include the observed cost, baseline cost, absolute increase, percentage increase, and an explanation of the detection rule.

These thresholds are configurable design choices for the prototype, not universal definitions of a cloud billing anomaly.

## How Change Correlation Works

The investigation component compares detected anomalies with recorded infrastructure events.

It considers factors such as:

- Whether the event affects the same resource.
- How close the event occurred to the anomaly.
- Whether the event falls within the investigation time window.

Candidates receive relevance scores to help prioritize investigation. The system does **not** claim that a correlated change caused the anomaly; correlation is evidence for further investigation, not proof of causation.

## Getting Started

### Prerequisites

- Python 3.11 or newer, with a compatible environment for the pinned dependencies
- Node.js and npm
- Git

The project was developed and tested locally on macOS with Python 3.14.

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd cloud-cost-intelligence
```

Replace `<YOUR_REPOSITORY_URL>` with your repository URL.

### 2. Set up Python

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

### 3. Generate sample data

From the project root:

```bash
python src/generate_data.py
python src/generate_events.py
```

These scripts generate the synthetic billing records and simulated infrastructure change events used by the prototype.

### 4. Generate the analysis reports

```bash
python src/analyzer.py
python src/change_correlator.py
```

The resulting reports are written to `sample-data/` and consumed by the API.

### 5. Start the backend

In one terminal, from the project root with the virtual environment activated:

```bash
python -m uvicorn src.api:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

Useful endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Check backend health |
| `GET /api/overview` | Retrieve the cost analysis report |
| `GET /api/investigations` | Retrieve anomaly investigation results |
| `POST /api/refresh` | Regenerate analysis and investigation reports |

### 6. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, normally `http://localhost:5173`.

The frontend uses `VITE_API_URL` to configure the backend address. For local development, the value is:

```text
VITE_API_URL=http://127.0.0.1:8000
```

Create `frontend/.env` with this setting if it is not already present. Do not commit local environment files.

### Optional: Run the original Streamlit dashboard

From the project root:

```bash
streamlit run src/dashboard.py
```

## Testing

Run the automated test suite from the project root:

```bash
python -m pytest -v
```

The current suite contains 12 tests covering:

- Total spending calculations.
- Rejection of invalid billing records.
- Detection of large cost spikes.
- Stable spending without false anomaly triggers.
- Development resource recommendations.
- Ranking of potentially relevant change events.
- Exclusion of unrelated, old, and future events.

**Current test status:** 12 tests passed in the local development environment.

Build the frontend for production with:

```bash
cd frontend
npm run build
```

The production build compiles the TypeScript code and generates optimized frontend assets in `frontend/dist/`.

## Current Limitations

- Billing records are synthetic; the application is not connected to a live AWS account.
- Infrastructure change events are simulated.
- Correlation scores prioritize evidence but do not establish causation.
- Optimization recommendations are heuristic and do not currently quantify verified savings.
- The application is intended for local development and demonstration, not production deployment.

## Future Improvements

- Integrate AWS Cost and Usage Reports or another supported billing data source.
- Incorporate AWS resource metadata and real infrastructure change history.
- Improve anomaly detection with configurable thresholds and more historical context.
- Estimate potential savings and validate recommendations against actual resource usage.
- Add API integration tests and broader edge-case coverage.
- Deploy the application securely and add authentication, monitoring, and operational documentation.

## Project Goal

This project explores how software engineering, data analysis, and infrastructure context can help engineers investigate unexpected cloud spending and identify opportunities for cost optimization.

It is designed as a practical demonstration of analytical problem-solving, API development, frontend integration, data validation, and automated testing.
