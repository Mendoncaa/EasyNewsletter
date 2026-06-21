"""Tests for the summarizer module."""

from src.summarizer import _fallback_summary


class TestFallbackSummary:
    def test_basic_summary(self):
        content = "This is a first meaningful sentence about artificial intelligence and its future. Second important sentence about modern technology trends worldwide. Third sentence about news and global developments today. Fourth sentence that should be ignored entirely."
        result = _fallback_summary(content)
        lines = result.strip().split("\n")
        assert len(lines) == 3

    def test_short_content(self):
        content = "Only one long sentence about an important topic that matters."
        result = _fallback_summary(content)
        assert len(result) > 0

    def test_empty_content(self):
        assert _fallback_summary("") == "Conteúdo não disponível."

    def test_filters_short_segments(self):
        content = "OK. Yes. This is a real sentence about something important. Another real sentence here too. Short."
        result = _fallback_summary(content)
        # Should only pick sentences with 20+ chars
        assert "real sentence" in result
