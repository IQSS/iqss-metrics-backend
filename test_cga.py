import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import cga


class CgaEventRegistrationAggrTests(unittest.TestCase):
    def run_aggregation(self, rows, headers=None):
        if headers is None:
            headers = ["Timestamp", "The event name"]

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            with open(path / "cgaEventRegistration.tsv", "w") as tsv_file:
                writer = csv.DictWriter(tsv_file, fieldnames=headers, delimiter="\t")
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)

            with patch.object(
                cga,
                "get_beginning_of_this_year",
                return_value=pd.Timestamp(2026, 1, 1),
            ), patch.object(cga, "get_current_year_str", return_value="2026"):
                cga.cga_event_registration_aggr(f"{tmpdir}/")

            with open(path / "main_metrics.tsv") as metrics_file:
                return list(csv.DictReader(metrics_file, delimiter="\t"))

    def test_june_first_empty_rolling_window_counts_timestamp_ytd(self):
        rows = [
            {"Timestamp": "5/20/2025 14:01:34", "The event name": "CGA Conference 2025"},
            {"Timestamp": "5/21/2025 16:24:41", "The event name": "CGA Conference 2025"},
            {"Timestamp": "4/4/2026 9:41:28", "The event name": "CGA Conference 2025"},
        ]

        metrics = self.run_aggregation(rows)

        self.assertEqual(metrics[0]["value"], "1")
        self.assertEqual(metrics[0]["unit"], "Registrations for CGA Conference 2026 YTD")

    def test_no_current_year_rows_writes_zero(self):
        rows = [
            {"Timestamp": "5/20/2025 14:01:34", "The event name": "CGA Conference 2025"},
            {"Timestamp": "5/21/2025 16:24:41", "The event name": "CGA Conference 2025"},
        ]

        metrics = self.run_aggregation(rows)

        self.assertEqual(metrics[0]["value"], "0")

    def test_missing_required_column_raises_clear_schema_error(self):
        rows = [{"Timestamp": "4/4/2026 9:41:28"}]

        with self.assertRaisesRegex(
            ValueError,
            "cgaEventRegistration.tsv is missing required columns: The event name",
        ):
            self.run_aggregation(rows, headers=["Timestamp"])

    def test_invalid_timestamps_raise_clear_error(self):
        rows = [
            {"Timestamp": "not a date", "The event name": "CGA Conference 2026"},
            {"Timestamp": "", "The event name": "CGA Conference 2026"},
        ]

        with self.assertRaisesRegex(
            ValueError,
            "cgaEventRegistration.tsv has no parseable values in Timestamp",
        ):
            self.run_aggregation(rows)


if __name__ == "__main__":
    unittest.main()
