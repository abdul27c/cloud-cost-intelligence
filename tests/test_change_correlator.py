import unittest
from datetime import datetime

from change_correlator import score_candidate, investigate


class TestChangeCorrelation(unittest.TestCase):

    def setUp(self):
        self.anomaly = {
            "resource_id": "transfer-prod-out",
            "date": "2026-10-07",
            "baseline_daily_cost_usd": 5.00,
            "observed_daily_cost_usd": 30.00,
        }

    def create_event(self, resource_id, event_time, event_id="EVT-001"):
        return {
            "event_id": event_id,
            "change_id": "CHG-1001",
            "event_time": datetime.fromisoformat(event_time),
            "resource_id": resource_id,
            "event_type": "infrastructure_change",
            "description": "Test infrastructure change",
        }

    def test_same_resource_same_day_scores_highest(self):
        event = self.create_event(
            "transfer-prod-out",
            "2026-10-07T09:00:00",
        )

        result = score_candidate(self.anomaly, event)

        self.assertEqual(result["relevance_score"], 90)
        self.assertTrue(result["same_resource"])
        self.assertFalse(result["causation_confirmed"])

    def test_unrelated_resource_scores_lower(self):
        event = self.create_event(
            "lambda-prod-api",
            "2026-10-07T11:30:00",
        )

        result = score_candidate(self.anomaly, event)

        self.assertEqual(result["relevance_score"], 30)
        self.assertFalse(result["same_resource"])

    def test_future_event_is_excluded(self):
        event = self.create_event(
            "transfer-prod-out",
            "2026-10-09T10:00:00",
        )

        result = score_candidate(self.anomaly, event)

        self.assertIsNone(result)

    def test_old_event_is_excluded(self):
        event = self.create_event(
            "transfer-prod-out",
            "2026-09-20T10:00:00",
        )

        result = score_candidate(self.anomaly, event)

        self.assertIsNone(result)

    def test_relevant_change_ranks_first(self):
        events = [
            self.create_event(
                "lambda-prod-api",
                "2026-10-07T11:30:00",
                "EVT-001",
            ),
            self.create_event(
                "transfer-prod-out",
                "2026-10-07T09:00:00",
                "EVT-002",
            ),
        ]

        report = {"anomalies": [self.anomaly]}

        result = investigate(report, events)

        candidates = result["investigations"][0]["candidate_changes"]

        self.assertEqual(candidates[0]["event_id"], "EVT-002")
        self.assertEqual(candidates[0]["relevance_score"], 90)

    def test_no_events_returns_empty_candidates(self):
        report = {"anomalies": [self.anomaly]}

        result = investigate(report, [])

        self.assertEqual(
            result["investigations"][0]["candidate_changes"],
            [],
        )


if __name__ == "__main__":
    unittest.main()
