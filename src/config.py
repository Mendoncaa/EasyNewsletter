"""Configuration management for EasyNewsletter."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")


class Config:
    """Centralized configuration loaded from environment variables."""

    # Email
    EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    IMAP_SERVER: str = os.getenv("IMAP_SERVER", "imap.gmail.com")
    IMAP_PORT: int = int(os.getenv("IMAP_PORT", "993"))

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # RSS
    RSS_FEEDS: list[str] = [
        f.strip()
        for f in os.getenv("RSS_FEEDS", "").split(",")
        if f.strip()
    ]

    # Output
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "output"))

    @classmethod
    def validate(cls) -> list[str]:
        """Return list of missing required config values."""
        errors = []
        if not cls.EMAIL_ADDRESS:
            errors.append("EMAIL_ADDRESS not set")
        if not cls.EMAIL_PASSWORD:
            errors.append("EMAIL_PASSWORD not set")
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY not set")
        return errors
