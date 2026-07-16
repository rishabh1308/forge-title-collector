from __future__ import annotations

import argparse

from .collector import collect_titles


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch web-page titles into JSON.")
    parser.add_argument("urls", nargs="+", help="One or more absolute http(s) URLs")
    parser.add_argument("--output", default="output/titles.json", help="Output JSON path")
    args = parser.parse_args()
    results = collect_titles(args.urls, args.output)
    for result in results:
        label = result.title if result.status == "success" else result.error
        print(f"[{result.status}] {result.url} — {label}")
    print(f"Wrote {len(results)} result(s) to {args.output}")
    return 0 if all(result.status == "success" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
