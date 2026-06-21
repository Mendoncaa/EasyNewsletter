"""Tests for the aggregator module."""

from datetime import datetime, timezone
from unittest.mock import patch

from src.aggregator import Article, _email_to_article, _rss_to_article, aggregate_all
from src.email_reader import RawEmail
from src.rss_reader import RSSArticle


class TestEmailToArticle:
    def test_converts_correctly(self):
        raw = RawEmail(
            subject="Test Newsletter",
            sender="test@example.com",
            date=datetime(2026, 6, 21, 10, 0, tzinfo=timezone.utc),
            html_body="<p>Hello World</p>",
            text_body="Hello World",
        )
        article = _email_to_article(raw)
        assert article.title == "Test Newsletter"
        assert article.source == "test@example.com"
        assert article.origin == "email"
        assert "Hello World" in article.content

    def test_prefers_html(self):
        raw = RawEmail(
            subject="Test",
            sender="s@e.com",
            date=None,
            html_body="<p>HTML version</p>",
            text_body="Plain version",
        )
        article = _email_to_article(raw)
        assert "HTML version" in article.content


class TestRssToArticle:
    def test_converts_correctly(self):
        rss = RSSArticle(
            title="RSS Title",
            source="HN",
            date=datetime(2026, 6, 20, 8, 0),
            content="Article content here.",
            link="https://example.com",
        )
        article = _rss_to_article(rss)
        assert article.title == "RSS Title"
        assert article.origin == "rss"
        assert article.date_str == "2026-06-20 08:00"


class TestArticleDateStr:
    def test_with_date(self):
        a = Article("T", "S", datetime(2026, 1, 15, 9, 30), "c", "rss")
        assert a.date_str == "2026-01-15 09:30"

    def test_without_date(self):
        a = Article("T", "S", None, "c", "rss")
        assert a.date_str == "Data desconhecida"
