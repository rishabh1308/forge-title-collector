"""Fetch and persist web-page titles."""

from .collector import CollectionResult, collect_titles, fetch_title

__all__ = ["CollectionResult", "collect_titles", "fetch_title"]
