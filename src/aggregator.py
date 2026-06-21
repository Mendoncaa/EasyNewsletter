"""Unified content model and aggregator for email + RSS sources."""

from dataclasses import dataclass

from src.email_reader import fetch_newsletters, RawEmail
from src.html_parser import clean_email_content
from src.rss_reader import fetch_rss_articles, RSSArticle
from src.config import Config


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

    # Sort by date (newest first), unknowns at the end
    articles.sort(key=lambda a: a.date if a.date != "Data desconhecida" else "", reverse=True)

    # Apply article limit (prioritize newest)
    total_before = len(articles)
    if Config.MAX_ARTICLES and len(articles) > Config.MAX_ARTICLES:
        articles = articles[:Config.MAX_ARTICLES]

    print(f"\n📊 Total agregado: {len(articles)} artigos ({sum(1 for a in articles if a.origin == 'email')} emails + {sum(1 for a in articles if a.origin == 'rss')} RSS)", end="")
    if total_before > len(articles):
        print(f" — limitado de {total_before} para {len(articles)}")
    else:
        print()
    return articles
