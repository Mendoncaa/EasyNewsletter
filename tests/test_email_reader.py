"""Tests for the email reader module (unit tests only, no IMAP connection)."""

import email
from src.email_reader import _decode_header_value, _extract_body, _parse_date


class TestDecodeHeaderValue:
    def test_plain_ascii(self):
        assert _decode_header_value("Hello World") == "Hello World"

    def test_empty_string(self):
        assert _decode_header_value("") == ""

    def test_encoded_utf8(self):
        # RFC 2047 encoded header
        encoded = "=?utf-8?B?T2zDoSBNdW5kbw==?="
        result = _decode_header_value(encoded)
        assert "Olá Mundo" in result


class TestExtractBody:
    def test_simple_text_email(self):
        msg = email.message.Message()
        msg.set_type("text/plain")
        msg.set_payload(b"Hello plain text", charset="utf-8")
        html, text = _extract_body(msg)
        assert text == "Hello plain text"
        assert html == ""

    def test_simple_html_email(self):
        msg = email.message.Message()
        msg.set_type("text/html")
        msg.set_payload(b"<p>Hello HTML</p>", charset="utf-8")
        html, text = _extract_body(msg)
        assert "<p>Hello HTML</p>" in html
        assert text == ""


class TestParseDate:
    def test_valid_date(self):
        msg = email.message.Message()
        msg["Date"] = "Sat, 21 Jun 2026 10:30:00 +0000"
        result = _parse_date(msg)
        assert "2026-06-21" in result

    def test_missing_date(self):
        msg = email.message.Message()
        result = _parse_date(msg)
        assert result == "Data desconhecida"
