"""Markdown digest generator using Jinja2 templates."""

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.config import Config


def generate_digest(summarized_articles: list[dict]) -> Path:
    """Generate a daily Markdown digest file from summarized articles.

    Args:
        summarized_articles: List of dicts with keys:
            title, source, date, summary, origin.

    Returns:
        Path to the generated .md file.
    """
    # Setup Jinja2
    templates_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("daily_digest.md.j2")

    # Split articles by origin
    email_articles = [a for a in summarized_articles if a["origin"] == "email"]
    rss_articles = [a for a in summarized_articles if a["origin"] == "rss"]

    now = datetime.now()
    content = template.render(
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M"),
        email_articles=email_articles,
        rss_articles=rss_articles,
        total=len(summarized_articles),
    )

    # Write output file
    output_dir = Config.OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"digest_{now.strftime('%Y-%m-%d')}.md"
    output_file.write_text(content, encoding="utf-8")

    print(f"   📄 Digest gerado: {output_file}")
    return output_file