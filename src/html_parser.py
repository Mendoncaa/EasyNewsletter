"""HTML to clean text parser for newsletter emails."""

import re

from bs4 import BeautifulSoup
import html2text


# Tags that typically contain newsletter noise (tracking, ads, footers)
NOISE_TAGS = ["script", "style", "noscript", "iframe", "img"]
NOISE_CLASSES = [
    "footer", "unsubscribe", "tracking", "advertisement",
    "social-links", "email-footer", "mso", "preheader",
]


def _remove_noise(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove tracking pixels, scripts, styles, and ad-related elements."""
    # Remove noise tags entirely
    for tag in NOISE_TAGS:
        for el in soup.find_all(tag):
            el.decompose()

    # Remove elements with noise-related class names
    for el in soup.find_all(attrs={"class": True}):
        class_attr = el.get("class") if el.attrs else None
        if not class_attr:
            continue
        classes = " ".join(class_attr) if isinstance(class_attr, list) else str(class_attr)
        if any(noise in classes.lower() for noise in NOISE_CLASSES):
            el.decompose()

    # Remove hidden elements
    for el in soup.find_all(style=re.compile(r"display\s*:\s*none", re.I)):
        el.decompose()

    # Remove tracking pixels (1x1 images)
    for img in soup.find_all("img"):
        width = img.get("width", "")
        height = img.get("height", "")
        if width in ("1", "0") or height in ("1", "0"):
            img.decompose()

    return soup


def html_to_clean_text(html: str) -> str:
    """Convert HTML email content to clean, readable plain text.

    Args:
        html: Raw HTML string from an email body.

    Returns:
        Clean plain text suitable for summarization.
    """
    if not html or not html.strip():
        return ""

    # Parse and clean HTML
    soup = BeautifulSoup(html, "html.parser")
    soup = _remove_noise(soup)

    # Convert to markdown-like text using html2text
    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.ignore_images = True
    converter.ignore_emphasis = False
    converter.body_width = 0  # No wrapping
    converter.skip_internal_links = True

    text = converter.handle(str(soup))

    # Post-processing cleanup
    text = re.sub(r"\n{3,}", "\n\n", text)  # Max 2 consecutive newlines
    text = re.sub(r"[ \t]+", " ", text)       # Collapse whitespace
    text = re.sub(r"^\s+$", "", text, flags=re.MULTILINE)  # Empty lines
    text = text.strip()

    return text


def clean_email_content(html_body: str, text_body: str) -> str:
    """Get clean text from an email, preferring HTML parsing over plain text.

    Args:
        html_body: HTML body of the email.
        text_body: Plain text body of the email.

    Returns:
        Cleaned text content.
    """
    if html_body:
        return html_to_clean_text(html_body)
    return text_body.strip() if text_body else ""