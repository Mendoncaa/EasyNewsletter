# 📰 EasyNewsletter - Agregador de Newsletter Pessoal

## Roadmap de Desenvolvimento

### Fase 1: Fundação
- [x] **Etapa 1.1** — Setup do projeto, estrutura de pastas, Git init, dependências
- [x] **Etapa 1.2** — Configuração segura (.env + config.py), gestão de credenciais

### Fase 2: Leitura de Emails (IMAP)
- [x] **Etapa 2.1** — Conexão IMAP ao Gmail, fetch de emails de newsletters
- [x] **Etapa 2.2** — Parsing de HTML de emails → texto limpo

### Fase 3: Leitura de RSS
- [x] **Etapa 3.1** — Leitor de feeds RSS/Atom configuráveis
- [x] **Etapa 3.2** — Normalização: interface unificada para conteúdo (email + RSS)

### Fase 4: Inteligência Artificial
- [x] **Etapa 4.1** — Integração com Ollama (local, gratuito) + OpenAI fallback
- [x] **Etapa 4.2** — Geração do ficheiro Markdown diário com template Jinja2

### Fase 5: Automação e Finalização
- [x] **Etapa 5.1** — Scheduling (execução diária) + entry point robusto
- [x] **Etapa 5.2** — Testes unitários + documentação final (README)

### Fase 6: Hardening (pós-review)
- [x] **Etapa 6.1** — Migração OpenAI → Ollama (sem custos, sem API keys)
- [x] **Etapa 6.2** — Fix: BS4 decompose crash em newsletters Substack complexas
- [x] **Etapa 6.3** — Fix: _parse_date crash em datas malformadas
- [x] **Etapa 6.4** — Fix: NOISE_TAGS dead code + table artifact cleanup
- [x] **Etapa 6.5** — Resiliência: pipeline continua mesmo se 1 email falhar

### Fase 7: Qualidade de Conteúdo
- [x] **Etapa 7.1** — Filtro inteligente: List-Unsubscribe header (RFC 2369)
- [x] **Etapa 7.2** — Sender blacklist configurável (EMAIL_SENDER_BLACKLIST)
- [x] **Etapa 7.3** — Limite de artigos configurável (MAX_ARTICLES=20)

### Fase 8: Correções Críticas (plano de melhorias)
- [x] **Etapa 8.1** — Fix main() executava pipeline 2× (bloco if duplicado)
- [x] **Etapa 8.2** — IMAP two-phase fetch (headers primeiro, body só para newsletters)
- [x] **Etapa 8.3** — RSS com httpx timeout 15s (previne hangs em daemon mode)

### Fase 9: Robustez e Performance
- [x] **Etapa 9.1** — openai como dependência explícita no requirements
- [x] **Etapa 9.2** — SummarizedArticle dataclass (type safety, elimina dicts)
- [x] **Etapa 9.3** — Paralelizar RSS feeds (ThreadPoolExecutor, max_workers=4)
- [x] **Etapa 9.4** — Logging configurável (LOG_LEVEL env)
- [x] **Etapa 9.5** — Validação de resposta Ollama/OpenAI (.get() seguro)
- [x] **Etapa 9.6** — Truncagem unificada via Config.MAX_CONTENT_CHARS

### Fase 10: Manutenibilidade e Escalabilidade
- [x] **Etapa 10.1** — Estado persistente + deduplicação (.seen.json)
- [x] **Etapa 10.2** — Ordenação por datetime real (timezone-aware)
- [x] **Etapa 10.3** — Testes expandidos: 37 testes (state, aggregator, etc.)
- [x] **Etapa 10.4** — pyproject.toml + ruff lint + GitHub Actions CI
- [x] **Etapa 10.5** — Task Scheduler (Windows) + run_daily.bat

---

## Tech Stack
- **Linguagem:** Python 3.14
- **IMAP:** imaplib (stdlib, two-phase fetch)
- **RSS:** feedparser + httpx (parallel, timeout)
- **HTML Parsing:** beautifulsoup4 + html2text
- **IA (primário):** Ollama (llama3.2, local e gratuito)
- **IA (fallback):** OpenAI GPT-3.5-turbo (opcional)
- **HTTP:** httpx
- **Config:** python-dotenv
- **Templates:** jinja2
- **Scheduling:** Task Scheduler (Windows) / schedule (daemon)
- **Quality:** ruff + mypy + pytest (37 tests) + GitHub Actions CI
