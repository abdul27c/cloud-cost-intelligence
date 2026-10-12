import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "sample-data"

REPORT = DATA_DIR / "analysis_report.json"
INVESTIGATION_REPORT = DATA_DIR / "investigation_report.json"

ANALYZER = ROOT / "src" / "analyzer.py"
CORRELATOR = ROOT / "src" / "change_correlator.py"


st.set_page_config(
    page_title="Cloud Cost Intelligence",
    page_icon="☁️",
    layout="wide",
)

st.title("☁️ Cloud Cost Intelligence")
st.caption(
    "Cloud spending analytics, anomaly detection, and "
    "evidence-based change investigation"
)


def run_script(script_path):
    """Run a project script and return its result."""
    return subprocess.run(
        [sys.executable, str(script_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


if st.button("Refresh analysis", type="primary"):
    with st.spinner("Running cost analysis and change investigation..."):
        result = run_script(ANALYZER)

        if result.returncode != 0:
            st.error("Cost analysis failed.")
            st.code(result.stderr)
            st.stop()

        result = run_script(CORRELATOR)

        if result.returncode != 0:
            st.error("Change investigation failed.")
            st.code(result.stderr)
            st.stop()

    st.success("Cost analysis and investigation reports refreshed.")
    st.rerun()


if not REPORT.exists():
    st.warning("No cost analysis report found.")
    st.code("python src/analyzer.py")
    st.stop()

with REPORT.open(encoding="utf-8") as file:
    report = json.load(file)

summary = report["summary"]
service_spend = report["spend_by_service_usd"]
anomalies = report["anomalies"]
recommendations = report["recommendations"]


# Overview metrics
m1, m2, m3, m4 = st.columns(4)

m1.metric("Total simulated spend", f"${summary['total_spend_usd']:,.2f}")
m2.metric("Valid records", summary["valid_records"])
m3.metric("Anomalies detected", len(anomalies))
m4.metric("Rejected billing records", summary["rejected_records"])

st.divider()


# Spending charts
left, right = st.columns([3, 2])

with left:
    st.subheader("Spending by cloud service")

    service_df = pd.DataFrame(
        [
            {"Service": name, "Cost (USD)": cost}
            for name, cost in service_spend.items()
        ]
    )

    if not service_df.empty:
        st.bar_chart(service_df.set_index("Service"))

with right:
    st.subheader("Daily spending trend")

    daily_df = pd.DataFrame(
        [
            {"Date": day, "Cost (USD)": cost}
            for day, cost in report["daily_spend_usd"].items()
        ]
    )

    if not daily_df.empty:
        daily_df["Date"] = pd.to_datetime(daily_df["Date"])
        st.line_chart(daily_df.set_index("Date"))


# Anomaly alerts
st.divider()
st.subheader("🚨 Cost anomaly alerts")

if anomalies:
    anomaly_df = pd.DataFrame(anomalies)
    st.dataframe(anomaly_df, use_container_width=True, hide_index=True)
else:
    st.success("No anomalies detected by the current rules.")


# Change investigation
st.divider()
st.subheader("🔎 Cost Anomaly Investigation")

st.write(
    "Review nearby deployment and infrastructure events to identify "
    "plausible explanations for unusual spending."
)

if not INVESTIGATION_REPORT.exists():
    st.warning(
        "The investigation report is missing. Click **Refresh analysis** "
        "to generate both reports."
    )
else:
    with INVESTIGATION_REPORT.open(encoding="utf-8") as file:
        investigation_report = json.load(file)

    i1, i2, i3 = st.columns(3)
    i1.metric(
        "Anomalies investigated",
        investigation_report["anomalies_investigated"],
    )
    i2.metric(
        "Change events loaded",
        investigation_report["events_loaded"],
    )
    i3.metric(
        "Rejected change events",
        len(investigation_report.get("rejected_events", [])),
    )

    for investigation in investigation_report["investigations"]:
        anomaly = investigation["anomaly"]

        with st.container(border=True):
            st.markdown(
                f"### {anomaly['resource_id']} · {anomaly['date']}"
            )

            st.write(
                f"Observed cost: **${anomaly['observed_cost_usd']:,.2f}**"
                if "observed_cost_usd" in anomaly
                else "Review the anomaly table above for the observed cost."
            )

            candidates = investigation["candidate_changes"]

            if not candidates:
                st.info("No eligible nearby change events were found.")
                continue

            st.markdown("**Ranked candidate changes**")

            candidate_df = pd.DataFrame(
                [
                    {
                        "Score": candidate["relevance_score"],
                        "Change ID": candidate["change_id"],
                        "Event type": candidate["event_type"],
                        "Resource": candidate["resource_id"],
                        "Event time": candidate["event_time"],
                        "Assessment": candidate["assessment"],
                    }
                    for candidate in candidates
                ]
            )

            st.dataframe(
                candidate_df,
                use_container_width=True,
                hide_index=True,
            )

            for candidate in candidates:
                with st.expander(
                    f"{candidate['change_id']} — "
                    f"Score {candidate['relevance_score']}"
                ):
                    st.write(candidate["description"])
                    st.caption(
                        f"Event ID: {candidate['event_id']} · "
                        f"Type: {candidate['event_type']} · "
                        f"Resource: {candidate['resource_id']}"
                    )

                    st.markdown("**Evidence considered**")
                    for evidence in candidate["evidence"]:
                        st.markdown(f"- {evidence}")

                    st.caption(
                        "This score ranks candidate relevance; it is not "
                        "a probability that the event caused the anomaly."
                    )

            st.info(investigation["conclusion"])

    st.warning(
        "**Important limitation:** A temporal or resource match does not "
        "establish causation. Billing is aggregated by day, so same-day "
        "events cannot be reliably ordered against the onset of a cost spike."
    )

    if investigation_report.get("rejected_events"):
        with st.expander("Rejected change-event records"):
            st.dataframe(
                pd.DataFrame(investigation_report["rejected_events"]),
                use_container_width=True,
                hide_index=True,
            )


# Optimization recommendations
st.divider()
st.subheader("💡 Optimization recommendations")

if recommendations:
    for item in recommendations:
        with st.container(border=True):
            st.markdown(
                f"**{item['resource_id']}** · "
                f"Priority: {item['priority'].upper()}"
            )
            st.write(item["recommendation"])
            st.caption(item["evidence"])
            st.caption(
                "Potential savings have not been quantified; validate usage "
                "and pricing before making changes."
            )
else:
    st.info("No recommendations generated.")


# Data quality
with st.expander("Data quality details"):
    st.write(
        f"Analyzed {summary['days_analyzed']} distinct dates across "
        f"{summary['resources_analyzed']} resources."
    )

    if report["rejected_rows"]:
        st.dataframe(
            pd.DataFrame(report["rejected_rows"]),
            use_container_width=True,
            hide_index=True,
        )


st.caption(
    "Prototype using synthetic billing data and simulated change events. "
    "Findings are illustrative, not actual cloud billing or guaranteed savings."
)
