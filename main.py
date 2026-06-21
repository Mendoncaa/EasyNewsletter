"""EasyNewsletter - Entry Point.

Agregador de Newsletter Pessoal no Terminal / Markdown.

Usage:
    python main.py              # Run once (generate today's digest)
    python main.py --schedule   # Run daily at 07:00
    python main.py --days 3     # Look back 3 days
"""

import argparse
import logging
import os
import sys
import time as time_mod

import schedule

from src.aggregator import aggregate_all
from src.config import Config
from src.markdown_generator import generate_digest
from src.state import filter_unseen, load_seen, mark_seen, save_seen
from src.summarizer import summarize_batch

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "WARNING").upper(), logging.WARNING),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

def run_digest(days_back: int = 1) -> None:
    """Execute the full digest pipeline once."""
    print("=" * 50)
    print("📰 EasyNewsletter — A gerar digest...")
    print("=" * 50)

    # 1. Aggregate content
    articles = aggregate_all(days_back=days_back)
    if not articles:
        print("\n📭 Nenhum artigo encontrado. Nada a gerar.")
        return

    # 2. Deduplication — skip articles already seen
    seen = load_seen()
    new_articles = filter_unseen(articles, seen)
    if not new_articles:
        print(f"\n📭 Todos os {len(articles)} artigos já foram vistos. Nada de novo.")
        return
    if len(new_articles) < len(articles):
        print(f"\n🔄 {len(articles) - len(new_articles)} artigos já vistos, {len(new_articles)} novos")

    # 3. Summarize only new articles
    print("\n🤖 A gerar resumos...")
    summarized = summarize_batch(new_articles)

    # 4. Generate Markdown
    print("\n📝 A gerar ficheiro Markdown...")
    output_path = generate_digest(summarized)

    # 5. Persist state
    seen = mark_seen(new_articles, seen)
    save_seen(seen)

    print("\n" + "=" * 50)
    print("✅ Digest gerado com sucesso!")
    print(f"   📄 {output_path}")
    print(f"   📊 {len(summarized)} artigos resumidos")
    print("=" * 50)


def main():
    """Parse arguments and run the newsletter aggregator."""
    parser = argparse.ArgumentParser(
        description="EasyNewsletter - Agregador de Newsletter Pessoal"
    )
    parser.add_argument(
        "--schedule", action="store_true",
        help="Run daily at 07:00 (daemon mode)"
    )
    parser.add_argument(
        "--days", type=int, default=1,
        help="Number of days to look back (default: 1)"
    )
    parser.add_argument(
        "--time", type=str, default="07:00",
        help="Time to run daily in schedule mode (default: 07:00)"
    )
    args = parser.parse_args()

    # Validate configuration
    errors = Config.validate()
    if errors:
        print("❌ Erros de configuração:")
        for err in errors:
            print(f"   - {err}")
        print("\n💡 Copia .env.example para .env e preenche as credenciais.")
        sys.exit(1)

    print("📰 EasyNewsletter")
    print(f"   Email: {Config.EMAIL_ADDRESS}")
    print(f"   Feeds RSS: {len(Config.RSS_FEEDS)} configurados")
    print(f"   Output: {Config.OUTPUT_DIR}/")

    if args.schedule:
        print(f"\n⏰ Modo agendado: todos os dias às {args.time}")
        schedule.every().day.at(args.time).do(run_digest, days_back=args.days)

        # Run immediately on first launch
        run_digest(days_back=args.days)

        while True:
            schedule.run_pending()
            time_mod.sleep(60)
    else:
        run_digest(days_back=args.days)


if __name__ == "__main__":
    main()
