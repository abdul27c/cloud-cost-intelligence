# Cloud Cost Intelligence & Optimization Platform

A Python-based cloud cost analytics prototype that analyzes billing records,
detects unusual spending, and produces evidence-based optimization suggestions.

## Business Problem

Cloud costs can increase unexpectedly when resources are overused, data
transfer spikes, or development environments run longer than necessary.
This project demonstrates a way to identify spending patterns and surface
potential optimization opportunities.

## Features

- Generate 90 days of synthetic cloud billing records.
- Validate records and report rejected rows.
- Calculate total spending and service-level cost breakdowns.
- Detect unusually large daily cost increases against a rolling median.
- Generate recommendations for reviewing development resources.
- Display metrics, trends, anomalies, and recommendations in a Streamlit dashboard.
- Run automated unit tests for core analytics behavior.

## Architecture

```text
Synthetic Billing Data (CSV)
            |
            v
    Data Validation
            |
            v
    Python Analytics Engine
       /          \
      v            v
Anomaly Detection  Optimization Recommendations
       \          /
            v
      JSON Analysis Report
            |
            v
     Streamlit Dashboard
```

## Tech Stack

- Python
- CSV and JSON
- Streamlit
- Pandas
- unittest
- Git

## Run Locally

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Generate sample data:

```bash
python src/generate_data.py
```

Run the analytics engine:

```bash
python src/analyzer.py
```

Launch the dashboard:

```bash
streamlit run src/dashboard.py
```

Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Data and Cost Disclaimer

The current prototype uses synthetic billing data. Cost values are illustrative
and do not represent actual AWS charges. Recommendations are suggestions for
investigation, not guaranteed savings or automated infrastructure changes.

## Current Limitations

- Anomaly detection uses a simple rolling-median threshold.
- Savings estimates are not yet calculated.
- AWS billing integrations and cloud deployment are not yet implemented.
- The sample dataset represents a small number of simulated resources.

## Future Improvements

- Integrate AWS Cost and Usage Report data.
- Add AWS storage, query, scheduling, and monitoring components.
- Improve anomaly detection and forecasting evaluation.
- Add infrastructure as code and CI/CD.
- Add evidence-grounded AI explanations with human review.
