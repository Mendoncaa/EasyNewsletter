"""Unified content model and aggregator for email + RSS sources."""

from dataclasses import dataclass
from datetime import datetime, timezone

from src.email_reader import RawEmail, fetch_newsletters
from src.html_parser import clean_email_content
from src.rss_reader import RSSArticle, fetch_rss_articles

# Sentinel for sorting: earliest possible aware datetime
_MIN_DATE = datetime.min.replace(tzinfo=timezone.utc)


@dataclass
class Article:
    """Normalized article from any source (email or RSS)."""
    title: str
    source: str
    date: datetime | None
    content: str
    origin: str  # "email" or "rss"

    @property
    def date_str(self) -> str:
        """Format date for display."""
        if self.date:
            return self.date.strftime("%Y-%m-%d %H:%M")
        return "Data desconhecida"


def _email_to_article(raw: RawEmail) -> Article:
    """Convert a RawEmail into a normalized Article."""
    clean = clean_email_content(raw.html_body, raw.text_body)

    return Article(
        title=raw.subject,
        source=raw.sender,
        date=raw.date,
        content=clean,
        origin="email",
    )


def _rss_to_article(rss: RSSArticle) -> Article:
    """Convert an RSSArticle into a normalized Article."""
    return Article(
        title=rss.title,
        source=rss.source,
        date=rss.date,
        content=rss.content,
        origin="rss",
    )


def aggregate_all(days_back: int = 1) -> list[Article]:
    """Fetch and normalize content from all sources.

    Args:
        days_back: Number of days to look back.

    Returns:
        List of normalized Article objects, sorted by date (newest first).
    """
    articles = []

    # Fetch from email
    print("\n📧 A processar emails...")
    try:
        raw_emails = fetch_newsletters(days_back=days_back)
        for e in raw_emails:
            try:
                articles.append(_email_to_article(e))
            except Exception as ex:
                print(f"   ⚠️ Erro ao processar email '{e.subject[:40]}': {ex}")
    except Exception as e:
        print(f"   ⚠️ Erro ao ler emails: {e}")

    # Fetch from RSS
    print("\n📡 A processar feeds RSS...")
    try:
        rss_articles = fetch_rss_articles(days_back=days_back)
        for a in rss_articles:
            try:
                articles.append(_rss_to_article(a))
            except Exception as ex:
                print(f"   ⚠️ Erro ao processar artigo RSS '{a.title[:40]}': {ex}")
    except Exception as e:
        print(f"   ⚠️ Erro ao ler feeds RSS: {e}")

    # Sort by date (newest first), None dates at the end
    def _sort_key(a: Article) -> datetime:
        if a.date is None:
            return _MIN_DATE
        # Normalize naive datetimes to UTC for comparison
        if a.date.tzinfo is None:
            return a.date.replace(tzinfo=timezone.utc)
        return a.date

    articles.sort(key=_sort_key, reverse=True)

    # Note: the MAX_ARTICLES limit is applied later (after deduplication) so
    # that already-seen articles don't consume slots reserved for new content.
    print(f"\n📊 Total agregado: {len(articles)} artigos ({sum(1 for a in articles if a.origin == 'email')} emails + {sum(1 for a in articles if a.origin == 'rss')} RSS)")
    return articles
