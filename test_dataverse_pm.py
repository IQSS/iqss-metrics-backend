import csv
from datetime import date, datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests

import dataverse_pm as pm


def response(data, next_url=None):
    result = Mock()
    result.json.return_value = data
    result.links = {"next": {"url": next_url}} if next_url else {}
    return result


class GithubTests(unittest.TestCase):
    def test_queries_and_release_pagination(self):
        day = date(2026, 1, 1)
        release = {"draft": False, "prerelease": False, "published_at": "2026-01-01T00:00:00Z"}
        replies = [response({"total_count": 1234, "incomplete_results": False}) for _ in range(7)]
        replies += [
            response([release, dict(release, draft=True), dict(release, prerelease=True)], "https://api.github.com/page2"),
            response([dict(release, published_at="2026-01-01T23:59:59Z"),
                      dict(release, published_at="2026-01-02T00:00:00Z"),
                      dict(release, published_at="2025-12-31T23:59:59Z")]),
            response([release]),
        ]
        with patch.object(pm, "_get", side_effect=replies) as get:
            metrics = pm._github_metrics(day)
        queries = [call.kwargs["params"]["q"] for call in get.call_args_list[:7]]
        self.assertEqual(queries, [
            "repo:IQSS/dataverse is:issue is:open",
            "repo:IQSS/dataverse is:pr is:open draft:false",
            "repo:IQSS/dataverse is:issue created:2026-01-01",
            "repo:IQSS/dataverse is:pr created:2026-01-01",
            "repo:IQSS/dataverse is:issue closed:2026-01-01",
            "repo:IQSS/dataverse is:pr merged:2026-01-01",
            'repo:IQSS/dataverse is:issue closed:2026-01-01 label:"Type: Bug"',
        ])
        self.assertEqual(metrics["github_open_issues"], 1234)
        self.assertEqual(metrics["dataverse_releases"], 2)
        self.assertEqual(metrics["dataverse_frontend_releases"], 1)
        self.assertEqual(get.call_args_list[8].args[0], "https://api.github.com/page2")

    def test_incomplete_search_is_not_accepted_as_a_count(self):
        with patch.object(pm, "_get", return_value=response({"total_count": 0, "incomplete_results": True})):
            with self.assertRaisesRegex(ValueError, "Incomplete GitHub search"):
                pm._github_metrics(date(2026, 10, 13))

    def test_http_errors_and_timeouts_are_not_hidden(self):
        reply = response({})
        reply.raise_for_status.side_effect = requests.HTTPError("503")
        with patch.object(pm.requests, "get", return_value=reply) as get:
            with self.assertRaises(requests.HTTPError):
                pm._get("https://example.org")
            get.assert_called_once_with("https://example.org", timeout=30)


class HubTests(unittest.TestCase):
    def test_variable_fractional_seconds_from_live_hub(self):
        for fraction in ["5", "56", "568", "5685", "56852", "568520"]:
            with self.subTest(fraction=fraction):
                parsed = pm._utc_timestamp("2026-10-13T05:59:05." + fraction)
                self.assertEqual(parsed.microsecond, int(fraction.ljust(6, "0")))
                self.assertEqual(parsed.tzinfo, timezone.utc)

    def test_discovery_month_rollover_latest_record_and_distinct_responders(self):
        old = {"recordDate": "2025-12-31T23:00:00", "dataverses": 10,
               "localDatasets": 20, "datasets": 999, "files": 30, "downloads": 40}
        latest = dict(old, recordDate="2026-01-01T06:00:00", localDatasets=21)
        replies = [
            response([{"hostname": "dataverse.harvard.edu", "dvHubId": "live-harvard-id"}]),
            response([
                {"dvHubId": "live-harvard-id", "metrics": [latest, old]},
                {"dvHubId": "another", "metrics": [latest, latest]},
                {"dvHubId": "stale", "metrics": [old]},
                {"dvHubId": "future", "metrics": [dict(old, recordDate="2026-02-01T00:00:00")]},
            ]),
            response({"installations": [{}, {}, {}, {}]}),
        ]
        with patch.object(pm, "_get", side_effect=replies) as get:
            result = pm._hub_metrics(date(2026, 1, 1))
        self.assertEqual(get.call_args_list[1].kwargs["params"], {"fromDate": "2025-12", "toDate": "2026-02"})
        self.assertEqual(result["installations_responding"], 2)
        self.assertEqual(result["installations_total"], 4)
        self.assertEqual(result["harvard_datasets"], 21)
        self.assertEqual(result["hub_record_date"], latest["recordDate"])
        self.assertEqual((result["harvard_collections"], result["harvard_files"], result["harvard_downloads"]), (10, 30, 40))
        self.assertTrue(all("headers" not in call.kwargs for call in get.call_args_list))

    def test_previous_month_observation_is_kept_with_its_real_date(self):
        record = {"recordDate": "2026-09-30T05:00:00", "dataverses": 1,
                  "localDatasets": 2, "files": 3, "downloads": 4}
        with patch.object(pm, "_get", side_effect=[
            response([{"hostname": "dataverse.harvard.edu", "dvHubId": "harvard"}]),
            response([{"dvHubId": "harvard", "metrics": [record]}]),
            response({"installations": [{}]}),
        ]):
            result = pm._hub_metrics(date(2026, 10, 1))
        self.assertEqual(result["installations_responding"], 0)
        self.assertEqual(result["hub_record_date"], record["recordDate"])

    def test_missing_harvard_metrics_fail_instead_of_writing_zero(self):
        with patch.object(pm, "_get", side_effect=[
            response([{"hostname": "dataverse.harvard.edu", "dvHubId": "harvard"}]), response([]),
        ]):
            with self.assertRaisesRegex(ValueError, "No Harvard Dataverse Hub observations"):
                pm._hub_metrics(date(2026, 10, 14))


class RtTests(unittest.TestCase):
    def test_utc_windows_whole_queue_and_unique_tickets(self):
        with patch.object(pm, "Rt") as client:
            tracker = client.return_value
            tracker.search.side_effect = [[{"id": "ticket/1"}, {"id": "ticket/1"}, {"id": "ticket/2"}], []]
            result = pm._rt_metrics(date(2025, 12, 31))
        self.assertEqual(result, {"rt_new": 2, "rt_closed": 0})
        calls = tracker.search.call_args_list
        self.assertEqual(calls[0].kwargs, {
            "Queue": "dataverse_support", "Format": "i",
            "raw_query": "Created >= '2025-12-31 00:00:00 UTC' AND Created < '2026-01-01 00:00:00 UTC'",
        })
        self.assertEqual(calls[1].kwargs["raw_query"],
                         "Resolved >= '2025-12-31 00:00:00 UTC' AND Resolved < '2026-01-01 00:00:00 UTC' AND Status = 'resolved'")
        self.assertEqual(tracker.session.request.keywords, {"timeout": 30})
        tracker.session.close.assert_called_once()

    def test_failed_login_is_not_a_zero(self):
        with patch.object(pm, "Rt") as client:
            client.return_value.login.return_value = False
            with self.assertRaisesRegex(RuntimeError, "could not log in"):
                pm._rt_metrics(date(2026, 10, 13))
            client.return_value.search.assert_not_called()


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.row = dict.fromkeys(pm.COLUMNS[2:], 1)
        self.row.update(date="2026-10-13", hub_record_date="2026-10-12T05:00:00")

    def test_first_run_history_and_same_day_replacement(self):
        target = pm._write_history(self.directory.name, self.row)
        today = dict(self.row, date="2026-10-14", rt_new=2)
        pm._write_history(self.directory.name, today)
        pm._write_history(self.directory.name, dict(today, rt_new=3))
        with target.open() as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            self.assertEqual(reader.fieldnames, pm.COLUMNS)
            rows = list(reader)
        self.assertEqual([row["date"] for row in rows], ["2026-10-13", "2026-10-14"])
        self.assertEqual([row["rt_new"] for row in rows], ["1", "3"])
        before = target.read_bytes()
        pm._write_history(self.directory.name, dict(today, rt_new=3))
        self.assertEqual(target.read_bytes(), before)

    def test_failed_collection_preserves_existing_history(self):
        target = pm._write_history(self.directory.name, self.row)
        before = target.read_bytes()
        with patch.object(pm, "_github_metrics", return_value={}), \
                patch.object(pm, "_hub_metrics", side_effect=requests.Timeout("Hub timeout")):
            with self.assertRaises(requests.Timeout):
                pm.harvest_dataverse_pm(self.directory.name)
        self.assertEqual(target.read_bytes(), before)

    def test_failed_write_preserves_history_and_cleans_temporary_file(self):
        target = pm._write_history(self.directory.name, self.row)
        before = target.read_bytes()
        with patch.object(csv.DictWriter, "writerows", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                pm._write_history(self.directory.name, dict(self.row, date="2026-10-14"))
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(list(Path(self.directory.name).iterdir()), [target])

    def test_unknown_history_schema_is_preserved(self):
        target = Path(self.directory.name) / pm.FILENAME
        target.write_text("unexpected\tcolumns\n")
        with self.assertRaisesRegex(ValueError, "Unexpected columns"):
            pm._write_history(self.directory.name, self.row)
        self.assertEqual(target.read_text(), "unexpected\tcolumns\n")

    def test_collection_uses_utc_and_previous_day_and_rejects_invalid_counts(self):
        with patch.object(pm, "datetime") as clock, \
                patch.object(pm, "_github_metrics", return_value={k: v for k, v in self.row.items() if k != "date"}) as github, \
                patch.object(pm, "_hub_metrics", return_value={}) as hub, \
                patch.object(pm, "_rt_metrics", return_value={}) as rt:
            clock.now.return_value = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
            target = pm.harvest_dataverse_pm(self.directory.name)
            with target.open() as stream:
                self.assertEqual(next(csv.DictReader(stream, delimiter="\t"))["date"], "2026-01-01")
            clock.now.assert_called_once_with(timezone.utc)
            github.assert_called_once_with(date(2025, 12, 31))
            hub.assert_called_once_with(date(2026, 1, 1))
            rt.assert_called_once_with(date(2025, 12, 31))
            for bad in [None, -1, True, "0"]:
                with self.subTest(bad=bad):
                    github.return_value = {k: v for k, v in dict(self.row, rt_new=bad).items() if k != "date"}
                    with self.assertRaisesRegex(ValueError, "Invalid Dataverse PM count"):
                        pm.harvest_dataverse_pm(self.directory.name)


if __name__ == "__main__":
    unittest.main()
