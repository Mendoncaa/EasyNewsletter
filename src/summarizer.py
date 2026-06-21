"""AI-powered article summarizer using Ollama (local) or OpenAI."""

import re
from dataclasses import dataclass

import httpx

from src.config import Config
from src.aggregator import Article

SYSTEM_PROMPT = """You are a newspaper editor. Generate a concise summary in EXACTLY 3 lines for the provided article.
Rules:
- Each line must be a complete, informative sentence
- Use clear and accessible language
- Keep key facts and important data
- Respond in the SAME language as the original article
- Do NOT use bullets, numbering, or special formatting
- Output ONLY the 3 lines, nothing else"""


@dataclass
class SummarizedArticle:
    """Article with AI-generated summary."""
    title: str
    source: str
    date: str
    summary: str
    origin: str


def _truncate(content: str) -> str:
    """Truncate content to configured max chars for AI input."""
    limit = Config.MAX_CONTENT_CHARS
    if len(content) > limit:
        return content[:limit]
    return content


def _call_ollama(title: str, content: str) -> str | None:
    """Call Ollama local API for summarization."""
    try:
        response = httpx.post(
            f"{Config.OLLAMA_URL}/api/chat",
            json={
                "model": Config.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Title: {title}\n\nContent:\n{_truncate(content)}"},
                ],
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 200},
            },
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()
        # Validate response schema
        message = data.get("message")
        if not message or not isinstance(message, dict):
            return None
        text = message.get("content")
        return text.strip() if text else None
    except httpx.ConnectError:
        print("   ⚠️ Ollama não está a correr. Inicia com: ollama serve")
        return None
    except httpx.TimeoutException:
        print(f"   ⚠️ Ollama timeout (60s) para '{title[:30]}'")
        return None
    except Exception as e:
        print(f"   ⚠️ Erro Ollama: {e}")
        return None


def _call_openai(title: str, content: str) -> str | None:
    """Call OpenAI API for summarization."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Title: {title}\n\nContent:\n{_truncate(content)}"},
            ],
            max_tokens=200,
            temperature=0.3,
        )
        choice = response.choices[0] if response.choices else None
        if not choice or not choice.message:
            return None
        return choice.message.content.strip() if choice.message.content else None
    except ImportError:
        print("   ⚠️ openai não instalado. Instala com: pip install openai")
        return None
    except Exception as e:
        print(f"   ⚠️ Erro OpenAI: {e}")
        return None


def _detect_ai_backend() -> str:
    """Detect which AI backend to use. Priority: Ollama > OpenAI > fallback."""
    if Config.OLLAMA_URL:
        try:
            r = httpx.get(f"{Config.OLLAMA_URL}/api/tags", timeout=3.0)
            if r.status_code == 200:
                return "ollama"
        except (httpx.ConnectError, httpx.TimeoutException):
            pass

    if Config.OPENAI_API_KEY and not Config.OPENAI_API_KEY.startswith("sk-your"):
        return "openai"

    return "fallback"


def summarize_article(article: Article, backend: str) -> str:
    """Generate a 3-line summary using the specified backend."""
    result = None

    if backend == "ollama":
        result = _call_ollama(article.title, article.content)
    elif backend == "openai":
        result = _call_openai(article.title, article.content)

    return result if result else _fallback_summary(article.content)


def summarize_batch(articles: list[Article]) -> list[SummarizedArticle]:
    """Summarize a list of articles, returning typed SummarizedArticle list."""
    backend = _detect_ai_backend()
    labels = {"ollama": f"Ollama ({Config.OLLAMA_MODEL})", "openai": "OpenAI", "fallback": "fallback (sem IA)"}
    print(f"   🤖 Modo de resumo: {labels[backend]}")

    results = []
    for i, article in enumerate(articles):
        print(f"   📝 [{i+1}/{len(articles)}] {article.title[:50]}...")
        summary = summarize_article(article, backend)
        results.append(SummarizedArticle(
            title=article.title,
            source=article.source,
            date=article.date_str,
            summary=summary,
            origin=article.origin,
        ))

    return results


def _fallback_summary(content: str) -> str:
    """Extract first 3 meaningful sentences as a basic summary."""
    if not content:
        return "Conteúdo não disponível."

    # Use regex for better sentence splitting (handles URLs, abbreviations)
    text = content.replace("\n", " ")
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    meaningful = [s.strip() for s in sentences if len(s.strip()) > 30]

    if not meaningful:
        return content[:300].strip() + "..."

    return "\n".join(meaningful[:3])