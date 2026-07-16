"""Quality gate: verify the collector works without external network access."""

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from title_collector.collector import collect_titles


def main() -> int:
    with TemporaryDirectory() as directory, patch("title_collector.collector.fetch_title", return_value="Health OK"):
        results = collect_titles(["https://health.test"], Path(directory) / "titles.json")
    assert results[0].status == "success"
    print("health check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
