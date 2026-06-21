"""Tests for the state/deduplication module."""

from dataclasses import dataclass
from datetime import datetime
from unittest.mock import patch

from src.state import _article_hash, filter_unseen, load_seen, mark_seen, save_seen

_DAY = datetime(2026, 6, 21, 10, 0)


@dataclass
class FakeArticle:
    title: str
    source: str
    date: datetime | None = _DAY


class TestArticleHash:
    def test_deterministic(self):
        h1 = _article_hash(FakeArticle("Title", "Source"))
        h2 = _article_hash(FakeArticle("Title", "Source"))
        assert h1 == h2

    def test_case_insensitive(self):
        h1 = _article_hash(FakeArticle("My Title", "My Source"))
        h2 = _article_hash(FakeArticle("my title", "my source"))
        assert h1 == h2

    def test_different_articles(self):
        h1 = _article_hash(FakeArticle("Title A", "Source"))
        h2 = _article_hash(FakeArticle("Title B", "Source"))
        assert h1 != h2

    def test_whitespace_normalized(self):
        h1 = _article_hash(FakeArticle("  Title  ", "  Source  "))
        h2 = _article_hash(FakeArticle("Title", "Source"))
        assert h1 == h2

    def test_recurring_title_different_days(self):
        """Same subject on different days must NOT collide."""
        h1 = _article_hash(FakeArticle("Morning Briefing", "News", datetime(2026, 6, 21)))
        h2 = _article_hash(FakeArticle("Morning Briefing", "News", datetime(2026, 6, 22)))
        assert h1 != h2

    def test_missing_date(self):
        h = _article_hash(FakeArticle("Title", "Source", None))
        assert isinstance(h, str) and len(h) == 16


class TestLoadSaveSeen:
    def test_roundtrip(self, tmp_path):
        state_file = tmp_path / ".seen.json"
        with patch("src.state._state_file", return_value=state_file):
            save_seen({"abc123", "def456"})
            loaded = load_seen()
            assert loaded == {"abc123", "def456"}

    def test_load_missing_file(self, tmp_path):
        state_file = tmp_path / "nonexistent.json"
        with patch("src.state._state_file", return_value=state_file):
            result = load_seen()
            assert result == set()

    def test_load_corrupted_json(self, tmp_path):
        state_file = tmp_path / ".seen.json"
        state_file.write_text("not valid json{{{", encoding="utf-8")
        with patch("src.state._state_file", return_value=state_file):
            result = load_seen()
            assert result == set()


class TestFilterUnseen:
    def test_filters_seen(self):
        articles = [FakeArticle("A", "Src"), FakeArticle("B", "Src")]
        seen = {_article_hash(FakeArticle("A", "Src"))}
        result = filter_unseen(articles, seen)
        assert len(result) == 1
        assert result[0].title == "B"

    def test_all_new(self):
        articles = [FakeArticle("A", "Src"), FakeArticle("B", "Src")]
        result = filter_unseen(articles, set())
        assert len(result) == 2


class TestMarkSeen:
    def test_adds_to_set(self):
        articles = [FakeArticle("A", "Src")]
        seen = set()
        result = mark_seen(articles, seen)
        assert _article_hash(FakeArticle("A", "Src")) in result
