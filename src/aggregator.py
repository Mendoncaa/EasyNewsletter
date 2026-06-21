"""Unified content model and aggregator for email + RSS sources."""

from dataclasses import dataclass

from src.email_reader import fetch_newsletters, RawEmail
from src.html_parser import clean_email_content
from src.rss_reader import fetch_rss_articles, RSSArticle


@dataclass
class Article:
    """Normalized article from any source (email or RSS)."""
    title: str
    source: str
    date: str
    content: str
    origin: str  # "email" or "rss"


def _email_to_article(raw: RawEmail) -> Article:
    """Convert a RawEmail into a normalized Article."""
    clean = clean_email_content(raw.html_body, raw.text_body)
    # Truncate very long content to save tokens for summarization
    if len(clean) > 5000:
        clean = clean[:5000] + "\n\n[... conteúdo truncado]"

    return Article(
        title=raw.subject,
        source=raw.sender,
        date=raw.date,
        content=clean,
        origin="email",
    )


def _rss_to_article(rss: RSSArticle) -> Article:
    """Convert an RSSArticle into a normalized Article."""
    content = rss.content
    if len(content) > 5000:
        content = content[:5000] + "\n\n[... conteúdo truncado]"

    return Article(
        title=rss.title,
        source=rss.source,
        date=rss.date,
        content=content,
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
        articles.extend(_email_to_article(e) for e in raw_emails)
    except Exception as e:
        print(f"   ⚠️ Erro ao ler emails: {e}")

    # Fetch from RSS
    print("\n📡 A processar feeds RSS...")
    try:
        rss_articles = fetch_rss_articles(days_back=days_back)
        articles.extend(_rss_to_article(a) for a in rss_articles)
    except Exception as e:
        print(f"   ⚠️ Erro ao ler feeds RSS: {e}")

    # Sort by date (newest first), unknowns at the end
    articles.sort(key=lambda a: a.date if a.date != "Data desconhecida" else "", reverse=True)

    print(f"\n📊 Total agregado: {len(articles)} artigos ({sum(1 for a in articles if a.origin == 'email')} emails + {sum(1 for a in articles if a.origin == 'rss')} RSS)")
    return articles
