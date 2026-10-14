from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests

import google_sheets


class GoogleSheetDownloadTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.target = Path(self.directory.name) / "training.tsv"
        self.target.write_text("date\tcount\n2026-10-13\t6\n")
        self.original = self.target.read_bytes()

    def harvest(self, text, content_type, status=200):
        reply = Mock(text=text, headers={"Content-Type": content_type})
        if status >= 400:
            reply.raise_for_status.side_effect = requests.HTTPError(str(status))
        with patch.object(google_sheets.http, "get", return_value=reply) as get:
            google_sheets.harvest_sheet_tsv_http(
                self.directory.name, "training", "https://example.org/sheet", "A:B", [0, 1], gid=123,
            )
        self.assertEqual(get.call_args.kwargs["timeout"], 30)
        return reply

    def test_html_error_preserves_existing_tsv(self):
        with self.assertLogs(level="WARNING") as logs:
            reply = self.harvest("<!DOCTYPE html><html>Page Not Found</html>", "text/html; charset=utf-8", 404)
        self.assertEqual(self.target.read_bytes(), self.original)
        self.assertIn("received HTML instead of TSV", logs.output[0])
        reply.raise_for_status.assert_not_called()

    def test_html_body_with_incorrect_content_type_is_skipped(self):
        self.harvest("\ufeff \n<HTML><body>Sign in</body></HTML>", "text/plain")
        self.assertEqual(self.target.read_bytes(), self.original)

    def test_html_does_not_create_a_new_file(self):
        self.target.unlink()
        self.harvest("<!doctype html><html>Not found</html>", "application/octet-stream")
        self.assertFalse(self.target.exists())

    def test_valid_tsv_replaces_existing_file(self):
        self.harvest("date\tcount\n2026-10-14\t7\n", "text/tab-separated-values; charset=utf-8")
        self.assertEqual(self.target.read_text(), "date\tcount\n2026-10-14\t7\n")

    def test_other_http_errors_preserve_existing_file_and_fail(self):
        with self.assertRaises(requests.HTTPError):
            self.harvest("Service unavailable", "text/plain", 503)
        self.assertEqual(self.target.read_bytes(), self.original)


if __name__ == "__main__":
    unittest.main()
