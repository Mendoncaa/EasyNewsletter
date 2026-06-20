"""EasyNewsletter - Entry Point.

Agregador de Newsletter Pessoal no Terminal / Markdown.
"""

from src.config import Config


def main():
    """Run the newsletter aggregator."""
    # Validate configuration
    errors = Config.validate()
    if errors:
        print("❌ Erros de configuração:")
        for err in errors:
            print(f"   - {err}")
        print("\n💡 Copia .env.example para .env e preenche as credenciais.")
        return

    print("📰 EasyNewsletter — A iniciar...")
    print(f"   Email: {Config.EMAIL_ADDRESS}")
    print(f"   Feeds RSS: {len(Config.RSS_FEEDS)} configurados")
    print(f"   Output: {Config.OUTPUT_DIR}/")
    print("\n✅ Configuração válida. Módulos em desenvolvimento...")


if __name__ == "__main__":
    main()
