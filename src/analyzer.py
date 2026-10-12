import csv
import json
import math
import statistics
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

INPUT = Path("sample-data/billing_records.csv")
OUTPUT = Path("sample-data/analysis_report.json")


def load_records(path=INPUT):
    """Load valid billing rows and report invalid rows."""
    valid = []
    rejected = []

    with path.open(newline="", encoding="utf-8") as file:
        for line_number, row in enumerate(csv.DictReader(file), start=2):
            try:
                usage_date = date.fromisoformat(row["usage_date"])
                quantity = float(row["usage_quantity"])
                cost = float(row["cost_usd"])

                if not math.isfinite(quantity) or not math.isfinite(cost):
                    raise ValueError("Quantity and cost must be finite numbers")

                if quantity < 0 or cost < 0:
                    raise ValueError("Quantity and cost must be non-negative")

                if not row["resource_id"] or not row["service"]:
                    raise ValueError("Missing resource ID or service")

                valid.append({
                    **row,
                    "usage_date": usage_date,
                    "usage_quantity": quantity,
                    "cost_usd": cost,
                })
            except (ValueError, TypeError, KeyError) as error:
                rejected.append({
                    "line": line_number,
                    "reason": str(error),
                })

    return valid, rejected


def analyze_records(records, rejected):
    """Calculate spending, detect spikes, and produce recommendations."""
    total_spend = round(sum(r["cost_usd"] for r in records), 2)

    service_totals = defaultdict(float)
    resource_totals = defaultdict(float)
    daily_totals = defaultdict(float)
    resource_daily = defaultdict(dict)
    resource_metadata = {}

    for row in records:
        service_totals[row["service"]] += row["cost_usd"]
        resource_totals[row["resource_id"]] += row["cost_usd"]
        daily_totals[row["usage_date"].isoformat()] += row["cost_usd"]
        resource_daily[row["resource_id"]][row["usage_date"]] = row["cost_usd"]
        resource_metadata[row["resource_id"]] = row

    service_report = {
        service: round(cost, 2)
        for service, cost in sorted(
            service_totals.items(), key=lambda item: item[1], reverse=True
        )
    }

    anomalies = []

    for resource_id, daily_costs in resource_daily.items():
        dates = sorted(daily_costs)
        if len(dates) < 15:
            continue

        for current_date in dates:
            # Compare a day's cost with the previous 14 calendar days.
            baseline_dates = [
                current_date - timedelta(days=offset)
                for offset in range(1, 15)
            ]
            baseline_values = [
                daily_costs[d] for d in baseline_dates if d in daily_costs
            ]

            if len(baseline_values) < 7:
                continue

            baseline = statistics.median(baseline_values)
            current = daily_costs[current_date]

            # Require both a large relative increase and a meaningful
            # absolute increase to avoid flagging tiny cost fluctuations.
            if baseline > 0 and current >= baseline * 3 and current - baseline >= 10:
                anomalies.append({
                    "resource_id": resource_id,
                    "date": current_date.isoformat(),
                    "baseline_daily_cost_usd": round(baseline, 2),
                    "observed_daily_cost_usd": round(current, 2),
                    "increase_usd": round(current - baseline, 2),
                    "increase_percent": round(
                        ((current - baseline) / baseline) * 100, 1
                    ),
                    "reason": "Daily cost was at least 3x its recent median.",
                })

    recommendations = []

    for resource_id, total in resource_totals.items():
        metadata = resource_metadata[resource_id]
        days_seen = len(resource_daily[resource_id])
        average_daily_cost = total / days_seen if days_seen else 0

        if metadata["environment"].lower() == "development":
            recommendations.append({
                "resource_id": resource_id,
                "priority": "medium",
                "recommendation": (
                    "Review whether this development resource can be stopped "
                    "outside working hours or scheduled automatically."
                ),
                "evidence": (
                    f"Development resource averaged "
                    f"${average_daily_cost:.2f} per observed day."
                ),
                "estimated_savings_usd": None,
                "note": "Savings require usage and pricing validation.",
            })

    return {
        "summary": {
            "valid_records": len(records),
            "rejected_records": len(rejected),
            "total_spend_usd": total_spend,
            "resources_analyzed": len(resource_totals),
            "days_analyzed": len(daily_totals),
        },
        "spend_by_service_usd": service_report,
        "daily_spend_usd": {
            day: round(cost, 2)
            for day, cost in sorted(daily_totals.items())
        },
        "anomalies": anomalies,
        "recommendations": recommendations,
        "rejected_rows": rejected,
    }


def main():
    records, rejected = load_records()
    report = analyze_records(records, rejected)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n=== CLOUD COST INTELLIGENCE REPORT ===")
    print(f"Valid records: {report['summary']['valid_records']}")
    print(f"Rejected records: {report['summary']['rejected_records']}")
    print(f"Total spend: ${report['summary']['total_spend_usd']:,.2f}")

    print("\nSpending by service:")
    for service, cost in report["spend_by_service_usd"].items():
        print(f"  {service:<15} ${cost:>10,.2f}")

    print(f"\nAnomalies detected: {len(report['anomalies'])}")
    for anomaly in report["anomalies"]:
        print(
            f"  {anomaly['resource_id']} on {anomaly['date']}: "
            f"${anomaly['observed_daily_cost_usd']:.2f} "
            f"(baseline ${anomaly['baseline_daily_cost_usd']:.2f})"
        )

    print(f"\nRecommendations: {len(report['recommendations'])}")
    for item in report["recommendations"]:
        print(f"  [{item['priority'].upper()}] {item['resource_id']}:")
        print(f"    {item['recommendation']}")

    print(f"\nFull report saved to {OUTPUT}")


if __name__ == "__main__":
    main()
