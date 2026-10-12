import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "sample-data" / "analysis_report.json"
ANALYZER = ROOT / "src" / "analyzer.py"

st.set_page_config(
    page_title="Cloud Cost Intelligence",
    page_icon="☁️",
    layout="wide",
)

st.title("☁️ Cloud Cost Intelligence")
st.caption(
    "Cloud spending analytics, anomaly detection, and optimization insights"
)

if st.button("Refresh analysis", type="primary"):
    result = subprocess.run(
        [sys.executable, str(ANALYZER)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        st.error("Analysis failed. Check the error details below.")
        st.code(result.stderr)
        st.stop()
    st.success("Analysis refreshed.")
    st.rerun()

if not REPORT.exists():
    st.warning("No report found. Run the analytics engine first.")
    st.code("python src/analyzer.py")
    st.stop()

with REPORT.open(encoding="utf-8") as file:
    report = json.load(file)

summary = report["summary"]
total_spend = summary["total_spend_usd"]
service_spend = report["spend_by_service_usd"]
anomalies = report["anomalies"]
recommendations = report["recommendations"]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total simulated spend", f"${total_spend:,.2f}")
m2.metric("Valid records", summary["valid_records"])
m3.metric("Anomalies detected", len(anomalies))
m4.metric("Rejected records", summary["rejected_records"])

st.divider()

left, right = st.columns([3, 2])

with left:
    st.subheader("Spending by cloud service")
    service_df = pd.DataFrame(
        [{"Service": name, "Cost (USD)": cost}
         for name, cost in service_spend.items()]
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

st.divider()
st.subheader("🚨 Cost anomaly alerts")

if anomalies:
    anomaly_df = pd.DataFrame(anomalies)
    st.dataframe(anomaly_df, use_container_width=True, hide_index=True)
else:
    st.success("No anomalies detected by the current rules.")

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
    "Demo uses synthetic billing data. Costs and findings are illustrative, "
    "not actual AWS billing or guaranteed savings."
)
