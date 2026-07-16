"""Small, dependency-free title collection service."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class _TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._inside_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._inside_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._inside_title = False

    def handle_data(self, data: str) -> None:
        if self._inside_title:
            self.parts.append(data)

    @property
    def title(self) -> str:
        return " ".join(unescape("".join(self.parts)).split())


@dataclass(frozen=True)
class CollectionResult:
    url: str
    title: str | None
    status: str
    error: str | None = None


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must be an absolute http(s) URL")


def fetch_title(url: str, timeout: float = 10.0) -> str:
    """Return a page title or raise a clear error."""
    _validate_url(url)
    request = Request(url, headers={"User-Agent": "ForgeTitleCollector/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get_content_type()
            if content_type not in {"text/html", "application/xhtml+xml"}:
                raise ValueError(f"Expected HTML but received {content_type}")
            encoding = response.headers.get_content_charset() or "utf-8"
            html = response.read().decode(encoding, errors="replace")
    except HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc

    parser = _TitleParser()
    parser.feed(html)
    if not parser.title:
        raise ValueError("No <title> element found")
    return parser.title


def collect_titles(urls: Iterable[str], output_path: str | Path) -> list[CollectionResult]:
    """Fetch each title and persist a deterministic JSON report."""
    results: list[CollectionResult] = []
    for url in urls:
        try:
            results.append(CollectionResult(url=url, title=fetch_title(url), status="success"))
        except (RuntimeError, ValueError) as exc:
            results.append(CollectionResult(url=url, title=None, status="failed", error=str(exc)))

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": [asdict(result) for result in results],
    }
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return results
