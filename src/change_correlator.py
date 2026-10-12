import csv
import json
from datetime import date, datetime
from pathlib import Path

REPORT_PATH = Path("sample-data/analysis_report.json")
EVENTS_PATH = Path("sample-data/change_events.csv")
OUTPUT_PATH = Path("sample-data/investigation_report.json")


def load_events(path=EVENTS_PATH):
    """Load and validate simulated deployment/change events."""
    events = []
    rejected = []

    with path.open(newline="", encoding="utf-8") as file:
        for line_number, row in enumerate(csv.DictReader(file), start=2):
            try:
                event_time = datetime.fromisoformat(row["event_time"])

                required = [
                    "event_id",
                    "resource_id",
                    "event_type",
                    "change_id",
                    "description",
                ]
                if any(not row.get(field, "").strip() for field in required):
                    raise ValueError("Required event field is missing")

                events.append({
                    **row,
                    "event_time": event_time,
                })
            except (ValueError, TypeError, KeyError) as error:
                rejected.append({
                    "line": line_number,
                    "reason": str(error),
                })

    return events, rejected


def score_candidate(anomaly, event):
    """Score a possible relationship without claiming causation."""
    anomaly_date = date.fromisoformat(anomaly["date"])
    event_date = event["event_time"].date()
    days_apart = (anomaly_date - event_date).days
    same_resource = anomaly["resource_id"] == event["resource_id"]

    # Events after the anomaly date cannot explain its initial onset.
    # Daily billing data cannot establish within-day event ordering.
    if days_apart < 0 or days_apart > 3:
        return None

    score = 0
    evidence = []

    if same_resource:
        score += 60
        evidence.append("Event affects the same resource as the anomaly.")

    if days_apart == 0:
        score += 30
        evidence.append("Event occurred on the anomaly date.")
    elif days_apart == 1:
        score += 15
        evidence.append("Event occurred one calendar day from the anomaly.")
    else:
        score += 5
        evidence.append(
            f"Event occurred {days_apart} calendar days from the anomaly."
        )

    if not same_resource:
        evidence.append(
            "Resource does not match; this event is weaker evidence."
        )

    if same_resource and days_apart == 0:
        assessment = "High-priority candidate"
    elif same_resource:
        assessment = "Related-resource candidate"
    elif days_apart == 0:
        assessment = "Same-day candidate; resource differs"
    else:
        assessment = "Low-priority candidate"

    return {
        "event_id": event["event_id"],
        "change_id": event["change_id"],
        "event_time": event["event_time"].isoformat(),
        "resource_id": event["resource_id"],
        "event_type": event["event_type"],
        "description": event["description"],
        "days_from_anomaly": days_apart,
        "same_resource": same_resource,
        "relevance_score": score,
        "assessment": assessment,
        "evidence": evidence,
        "causation_confirmed": False,
    }


def investigate(report, events):
    """Rank nearby changes for each detected cost anomaly."""
    investigations = []

    for anomaly in report.get("anomalies", []):
        candidates = []

        for event in events:
            candidate = score_candidate(anomaly, event)
            if candidate is not None:
                candidates.append(candidate)

        candidates.sort(
            key=lambda item: (
                item["relevance_score"],
                item["same_resource"],
                item["event_time"],
            ),
            reverse=True,
        )

        investigations.append({
            "anomaly": anomaly,
            "candidate_changes": candidates,
            "conclusion": (
                "Candidate changes are ranked by resource match and timing. "
                "These signals suggest what to investigate, but do not prove "
                "that a change caused the cost increase."
            ),
        })

    return {
        "source": "synthetic billing data and simulated change events",
        "anomalies_investigated": len(investigations),
        "events_loaded": len(events),
        "investigations": investigations,
    }


def main():
    with REPORT_PATH.open(encoding="utf-8") as file:
        report = json.load(file)

    events, rejected_events = load_events()
    result = investigate(report, events)
    result["rejected_events"] = rejected_events

    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print("\n=== COST ANOMALY INVESTIGATION ===")
    print(f"Anomalies investigated: {result['anomalies_investigated']}")
    print(f"Valid change events: {result['events_loaded']}")
    print(f"Rejected change events: {len(rejected_events)}")

    for investigation in result["investigations"]:
        anomaly = investigation["anomaly"]
        print(
            f"\nAnomaly: {anomaly['resource_id']} on {anomaly['date']}"
        )

        if not investigation["candidate_changes"]:
            print("  No nearby change events found.")
            continue

        for candidate in investigation["candidate_changes"]:
            print(
                f"  [{candidate['relevance_score']:>2}] "
                f"{candidate['change_id']} — {candidate['description']}"
            )
            print(f"      Assessment: {candidate['assessment']}")
            for evidence in candidate["evidence"]:
                print(f"      Evidence: {evidence}")

    print("\nImportant: candidate rankings do not establish causation.")
    print(f"Full investigation saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
