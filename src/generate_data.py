import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

OUTPUT = Path("sample-data/billing_records.csv")
DAYS = 90

RESOURCES = [
    {
        "service": "EC2",
        "environment": "production",
        "team": "platform",
        "resource_id": "ec2-prod-web",
        "base_cost": 18.00,
        "quantity": 24.0,
        "region": "us-east-1",
    },
    {
        "service": "EC2",
        "environment": "development",
        "team": "engineering",
        "resource_id": "ec2-dev-worker",
        "base_cost": 12.00,
        "quantity": 24.0,
        "region": "us-east-1",
    },
    {
        "service": "S3",
        "environment": "production",
        "team": "platform",
        "resource_id": "s3-prod-logs",
        "base_cost": 4.50,
        "quantity": 100.0,
        "region": "us-east-1",
    },
    {
        "service": "Lambda",
        "environment": "production",
        "team": "applications",
        "resource_id": "lambda-prod-api",
        "base_cost": 3.00,
        "quantity": 50000.0,
        "region": "us-east-1",
    },
    {
        "service": "DataTransfer",
        "environment": "production",
        "team": "platform",
        "resource_id": "transfer-prod-out",
        "base_cost": 5.00,
        "quantity": 50.0,
        "region": "us-east-1",
    },
]


def generate_records():
    records = []
    today = date.today()

    for day_offset in range(DAYS - 1, -1, -1):
        usage_date = today - timedelta(days=day_offset)

        for resource in RESOURCES:
            cost = resource["base_cost"] * random.uniform(0.92, 1.08)

            # Simulate gradual growth in production web-server spending.
            if resource["resource_id"] == "ec2-prod-web":
                elapsed_days = DAYS - 1 - day_offset
                cost *= 1 + (0.004 * elapsed_days)

            # Inject a known data-transfer spike for testing.
            if (
                resource["resource_id"] == "transfer-prod-out"
                and day_offset == 5
            ):
                cost *= 6

            records.append({
                "usage_date": usage_date.isoformat(),
                "service": resource["service"],
                "environment": resource["environment"],
                "team": resource["team"],
                "resource_id": resource["resource_id"],
                "usage_quantity": round(
                    resource["quantity"] * random.uniform(0.95, 1.05), 2
                ),
                "cost_usd": round(cost, 2),
                "region": resource["region"],
            })

    # Intentionally include one invalid record to test data validation.
    records.append({
        "usage_date": today.isoformat(),
        "service": "EC2",
        "environment": "development",
        "team": "engineering",
        "resource_id": "ec2-invalid-test",
        "usage_quantity": "not-a-number",
        "cost_usd": "invalid-cost",
        "region": "us-east-1",
    })

    return records


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    records = generate_records()

    fieldnames = [
        "usage_date",
        "service",
        "environment",
        "team",
        "resource_id",
        "usage_quantity",
        "cost_usd",
        "region",
    ]

    with OUTPUT.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {len(records)} billing records.")
    print(f"Saved to: {OUTPUT}")
    print(f"Includes {DAYS} days of data and one intentionally invalid record.")


if __name__ == "__main__":
    main()
