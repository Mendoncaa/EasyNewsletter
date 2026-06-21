"""Persistent state for deduplication — avoids re-summarizing seen articles."""

import hashlib
import json
from pathlib import Path

from src.config import Config


def _state_file() -> Path:
    """Path to the seen articles index."""
    return Config.OUTPUT_DIR / ".seen.json"


def _article_hash(article) -> str:
    """Generate a deterministic hash for deduplication.

    Includes the publication day so that newsletters with a recurring
    subject (e.g. "Your Morning Briefing") are not deduplicated across days
    while re-runs on the same day still collapse to the same hash.
    """
    day = article.date.strftime("%Y-%m-%d") if article.date else "no-date"
    normalized = f"{article.title.strip().lower()}|{article.source.strip().lower()}|{day}"
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def load_seen() -> set[str]:
    """Load the set of already-processed article hashes."""
    path = _state_file()
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return set(data.get("seen", []))
    except (json.JSONDecodeError, KeyError):
        return set()


def save_seen(seen: set[str]) -> None:
    """Persist the set of processed article hashes."""
    path = _state_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"seen": sorted(seen)}, indent=2),
        encoding="utf-8",
    )


def filter_unseen(articles: list, seen: set[str]) -> list:
    """Filter out articles that have already been processed.

    Args:
        articles: List of Article objects (must have .title, .source, .date).
        seen: Set of previously seen hashes.

    Returns:
        List of articles not yet seen.
    """
    unseen = []
    for article in articles:
        h = _article_hash(article)
        if h not in seen:
            unseen.append(article)
    return unseen


def mark_seen(articles: list, seen: set[str]) -> set[str]:
    """Add articles to the seen set. Returns the updated set."""
    for article in articles:
        h = _article_hash(article)
        seen.add(h)
    return seen
