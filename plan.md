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

---

## Tech Stack
- **Linguagem:** Python 3.14
- **IMAP:** imaplib (stdlib)
- **RSS:** feedparser
- **HTML Parsing:** beautifulsoup4 + html2text
- **IA (primário):** Ollama (llama3.2, local e gratuito)
- **IA (fallback):** OpenAI GPT-3.5-turbo (opcional)
- **HTTP:** httpx
- **Config:** python-dotenv
- **Templates:** jinja2
- **Scheduling:** schedule
