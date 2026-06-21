"""AI-powered article summarizer using OpenAI."""

from openai import OpenAI

from src.config import Config
from src.aggregator import Article

SYSTEM_PROMPT = """Eres un editor de jornal. Gera um resumo conciso em EXATAMENTE 3 linhas para o artigo fornecido.
Regras:
- Cada linha deve ser uma frase completa e informativa
- Usa linguagem clara e acessível
- Mantém os factos-chave e dados importantes
- Responde no mesmo idioma do artigo original
- NÃO uses bullets, numeração ou formatação especial"""


def summarize_article(article: Article) -> str:
    """Generate a 3-line summary of an article using OpenAI.

    Falls back to first 3 sentences if API key is not configured.
    """
    if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY.startswith("sk-your"):
        return _fallback_summary(article.content)

    try:
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Título: {article.title}\n\nConteúdo:\n{article.content[:3000]}"},
            ],
            max_tokens=200,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"   ⚠️ Erro OpenAI para '{article.title[:40]}': {e}")
        return _fallback_summary(article.content)


def summarize_batch(articles: list[Article]) -> list[dict]:
    """Summarize a list of articles, returning enriched dicts.

    Returns list of dicts with keys: title, source, date, summary, origin.
    """
    has_api = Config.OPENAI_API_KEY and not Config.OPENAI_API_KEY.startswith("sk-your")
    mode = "OpenAI" if has_api else "fallback (sem API key)"
    print(f"   🤖 Modo de resumo: {mode}")

    results = []
    for i, article in enumerate(articles):
        print(f"   📝 [{i+1}/{len(articles)}] {article.title[:50]}...")
        summary = summarize_article(article)
        results.append({
            "title": article.title,
            "source": article.source,
            "date": article.date,
            "summary": summary,
            "origin": article.origin,
        })

    return results


def _fallback_summary(content: str) -> str:
    """Extract first 3 meaningful sentences as a basic summary."""
    if not content:
        return "Conteúdo não disponível."

    # Split into sentences and filter noise
    lines = [
        line.strip()
        for line in content.replace("\n", " ").split(".")
        if len(line.strip()) > 20
    ]

    if not lines:
        return content[:200] + "..."

    sentences = [line.strip() + "." for line in lines[:3]]
    return "\n".join(sentences)