"""RSS/Atom feed reader for newsletter aggregation."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta
import time

import feedparser
import httpx

from src.config import Config
from src.html_parser import html_to_clean_text

logger = logging.getLogger(__name__)


@dataclass
class RSSArticle:
    """Article extracted from an RSS/Atom feed."""
    title: str
    source: str
    date: datetime | None
    content: str
    link: str


def _parse_entry_date(entry) -> datetime | None:
    """Extract datetime from a feed entry."""
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            return datetime.fromtimestamp(time.mktime(parsed))
    return None


def _extract_content(entry) -> str:
    """Extract the best available content from a feed entry."""
    # Try content field first (usually full article)
    if hasattr(entry, "content") and entry.content:
        html = entry.content[0].get("value", "")
        if html:
            return html_to_clean_text(html)

    # Fall back to summary/description
    summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
    if summary:
        return html_to_clean_text(summary)

    return ""


def fetch_rss_articles(days_back: int = 1) -> list[RSSArticle]:
    """Fetch articles from configured RSS feeds.

    Args:
        days_back: Only include articles from the last N days.

    Returns:
        List of RSSArticle objects with clean text content.
    """
    cutoff = datetime.now() - timedelta(days=days_back)
    feeds = Config.RSS_FEEDS
    articles = []

    print(f"   📡 A ler {len(feeds)} feeds RSS...")

    def _fetch_single_feed(feed_url: str) -> list[RSSArticle]:
        """Fetch and parse a single feed. Thread-safe."""
        result = []
        try:
            resp = httpx.get(
                feed_url, timeout=15.0, follow_redirects=True, verify=True
            )
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            feed_title = feed.feed.get("title", feed_url)

            for entry in feed.entries:
                entry_date = _parse_entry_date(entry)
                if entry_date and entry_date < cutoff:
                    continue

                content = _extract_content(entry)
                if not content:
                    continue

                date_str = entry_date.strftime("%Y-%m-%d %H:%M") if entry_date else "Data desconhecida"
                result.append(RSSArticle(
                    title=getattr(entry, "title", "Sem título"),
                    source=feed_title,
                    date=entry_date,
                    content=content,
                    link=getattr(entry, "link", ""),
                ))

            print(f"   ✅ {feed_title}: {len(result)} artigos")
        except httpx.TimeoutException:
            logger.warning(f"Timeout (15s) no feed: {feed_url}")
            print(f"   ⚠️ Timeout (15s) no feed: {feed_url}")
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP {e.response.status_code} no feed: {feed_url}")
            print(f"   ⚠️ HTTP {e.response.status_code} no feed: {feed_url}")
        except Exception as e:
            logger.exception(f"Erro no feed {feed_url}")
            print(f"   ⚠️ Erro no feed {feed_url}: {e}")
        return result

    # Fetch feeds in parallel (I/O-bound)
    with ThreadPoolExecutor(max_workers=min(4, len(feeds))) as pool:
        futures = {pool.submit(_fetch_single_feed, url): url for url in feeds}
        for future in as_completed(futures):
            articles.extend(future.result())

    print(f"   📰 Total: {len(articles)} artigos RSS")
    return articles