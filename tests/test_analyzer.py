import csv
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from analyzer import analyze_records, load_records


class TestBillingData(unittest.TestCase):
    def test_invalid_record_is_rejected(self):
        fields = [
            "usage_date", "service", "environment", "team",
            "resource_id", "usage_quantity", "cost_usd", "region",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "billing.csv"
            with path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
                writer.writerow({
                    "usage_date": "2026-10-01",
                    "service": "EC2",
                    "environment": "production",
                    "team": "platform",
                    "resource_id": "ec2-test",
                    "usage_quantity": "not-a-number",
                    "cost_usd": "10.00",
                    "region": "us-east-1",
                })

            valid, rejected = load_records(path)

        self.assertEqual(len(valid), 0)
        self.assertEqual(len(rejected), 1)

    def test_total_spending_is_calculated(self):
        records = [
            {
                "usage_date": date(2026, 10, 1),
                "service": "EC2",
                "environment": "production",
                "team": "platform",
                "resource_id": "ec2-test",
                "usage_quantity": 1.0,
                "cost_usd": 12.50,
                "region": "us-east-1",
            },
            {
                "usage_date": date(2026, 10, 1),
                "service": "S3",
                "environment": "production",
                "team": "platform",
                "resource_id": "s3-test",
                "usage_quantity": 1.0,
                "cost_usd": 2.50,
                "region": "us-east-1",
            },
        ]

        report = analyze_records(records, [])

        self.assertEqual(report["summary"]["total_spend_usd"], 15.00)
        self.assertEqual(report["spend_by_service_usd"]["EC2"], 12.50)
        self.assertEqual(report["spend_by_service_usd"]["S3"], 2.50)

    def test_large_cost_spike_is_detected(self):
        records = []
        start = date(2026, 9, 1)

        for day in range(20):
            records.append({
                "usage_date": start + timedelta(days=day),
                "service": "DataTransfer",
                "environment": "production",
                "team": "platform",
                "resource_id": "transfer-test",
                "usage_quantity": 1.0,
                "cost_usd": 30.00 if day == 19 else 5.00,
                "region": "us-east-1",
            })

        report = analyze_records(records, [])

        self.assertEqual(len(report["anomalies"]), 1)
        self.assertEqual(
            report["anomalies"][0]["observed_daily_cost_usd"], 30.00
        )

    def test_development_resource_gets_recommendation(self):
        records = [{
            "usage_date": date(2026, 10, 1),
            "service": "EC2",
            "environment": "development",
            "team": "engineering",
            "resource_id": "ec2-dev-test",
            "usage_quantity": 24.0,
            "cost_usd": 12.0,
            "region": "us-east-1",
        }]

        report = analyze_records(records, [])

        self.assertEqual(len(report["recommendations"]), 1)
        self.assertEqual(
            report["recommendations"][0]["resource_id"], "ec2-dev-test"
        )

    def test_non_finite_cost_is_rejected(self):
        fields = [
            "usage_date", "service", "environment", "team",
            "resource_id", "usage_quantity", "cost_usd", "region",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "billing.csv"
            with path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
                writer.writerow({
                    "usage_date": "2026-10-01",
                    "service": "EC2",
                    "environment": "production",
                    "team": "platform",
                    "resource_id": "ec2-test",
                    "usage_quantity": "1",
                    "cost_usd": "NaN",
                    "region": "us-east-1",
                })

            valid, rejected = load_records(path)

        self.assertEqual(len(valid), 0)
        self.assertEqual(len(rejected), 1)

    def test_stable_spending_does_not_trigger_anomaly(self):
        records = []
        start = date(2026, 9, 1)

        for day in range(20):
            records.append({
                "usage_date": start + timedelta(days=day),
                "service": "EC2",
                "environment": "production",
                "team": "platform",
                "resource_id": "ec2-stable",
                "usage_quantity": 1.0,
                "cost_usd": 5.00,
                "region": "us-east-1",
            })

        report = analyze_records(records, [])

        self.assertEqual(report["anomalies"], [])


if __name__ == "__main__":
    unittest.main()
