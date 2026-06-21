"""Tests for the state/deduplication module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from dataclasses import dataclass

from src.state import _article_hash, load_seen, save_seen, filter_unseen, mark_seen


@dataclass
class FakeArticle:
    title: str
    source: str


class TestArticleHash:
    def test_deterministic(self):
        h1 = _article_hash("Title", "Source")
        h2 = _article_hash("Title", "Source")
        assert h1 == h2

    def test_case_insensitive(self):
        h1 = _article_hash("My Title", "My Source")
        h2 = _article_hash("my title", "my source")
        assert h1 == h2

    def test_different_articles(self):
        h1 = _article_hash("Title A", "Source")
        h2 = _article_hash("Title B", "Source")
        assert h1 != h2

    def test_whitespace_normalized(self):
        h1 = _article_hash("  Title  ", "  Source  ")
        h2 = _article_hash("Title", "Source")
        assert h1 == h2


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
        seen = {_article_hash("A", "Src")}
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
        assert _article_hash("A", "Src") in result
