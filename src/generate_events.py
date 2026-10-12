import csv
from datetime import date, datetime, time, timedelta
from pathlib import Path

OUTPUT = Path("sample-data/change_events.csv")


def generate_events():
    today = date.today()
    spike_date = today - timedelta(days=5)

    return [
        {
            "event_id": "EVT-001",
            "event_time": datetime.combine(
                spike_date, time(9, 0)
            ).isoformat(),
            "resource_id": "transfer-prod-out",
            "event_type": "infrastructure_change",
            "change_id": "CHG-1042",
            "description": (
                "Outbound traffic routing configuration changed"
            ),
        },
        {
            "event_id": "EVT-002",
            "event_time": datetime.combine(
                spike_date - timedelta(days=1), time(14, 30)
            ).isoformat(),
            "resource_id": "ec2-prod-web",
            "event_type": "deployment",
            "change_id": "DEP-2081",
            "description": (
                "Production web application version deployed"
            ),
        },
        {
            "event_id": "EVT-003",
            "event_time": datetime.combine(
                spike_date, time(11, 30)
            ).isoformat(),
            "resource_id": "lambda-prod-api",
            "event_type": "deployment",
            "change_id": "DEP-2082",
            "description": (
                "Production API function version deployed"
            ),
        },
        {
            "event_id": "EVT-004",
            "event_time": datetime.combine(
                spike_date + timedelta(days=2), time(10, 0)
            ).isoformat(),
            "resource_id": "s3-prod-logs",
            "event_type": "configuration_change",
            "change_id": "CHG-1043",
            "description": (
                "Log retention configuration reviewed"
            ),
        },
    ]


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    events = generate_events()
    fields = [
        "event_id",
        "event_time",
        "resource_id",
        "event_type",
        "change_id",
        "description",
    ]

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(events)

    print(f"Generated {len(events)} change events.")
    print(f"Saved to: {OUTPUT}")
    print("Events are simulated for development and testing.")


if __name__ == "__main__":
    main()
