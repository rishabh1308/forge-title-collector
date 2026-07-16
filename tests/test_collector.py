from __future__ import annotations

import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from title_collector.collector import collect_titles, fetch_title


class FetchTitleTests(TestCase):
    @patch("title_collector.collector.urlopen")
    def test_fetches_and_normalizes_title(self, mock_urlopen: MagicMock) -> None:
        response = MagicMock()
        response.headers.get_content_type.return_value = "text/html"
        response.headers.get_content_charset.return_value = "utf-8"
        response.read.return_value = b"<html><title>  Forge &amp; NMG  </title></html>"
        mock_urlopen.return_value.__enter__.return_value = response
        self.assertEqual(fetch_title("https://example.test"), "Forge & NMG")

    def test_rejects_invalid_url(self) -> None:
        with self.assertRaisesRegex(ValueError, "absolute http"):
            fetch_title("example.com")

    @patch("title_collector.collector.fetch_title", side_effect=["One", ValueError("bad URL")])
    def test_persists_success_and_failure(self, _mock_fetch: MagicMock) -> None:
        destination = Path(self._testMethodName + ".json")
        self.addCleanup(destination.unlink, missing_ok=True)
        results = collect_titles(["https://one.test", "not-a-url"], destination)
        self.assertEqual([item.status for item in results], ["success", "failed"])
        payload = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(payload["results"][0]["title"], "One")
