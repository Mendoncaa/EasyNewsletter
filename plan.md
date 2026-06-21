# 📰 EasyNewsletter - Agregador de Newsletter Pessoal

## Roadmap de Desenvolvimento

### Fase 1: Fundação
- [x] **Etapa 1.1** — Setup do projeto, estrutura de pastas, Git init, dependências
- [x] **Etapa 1.2** — Configuração segura (.env + config.py), gestão de credenciais

### Fase 2: Leitura de Emails (IMAP)
- [ ] **Etapa 2.1** — Conexão IMAP ao Gmail, fetch de emails de newsletters ✅ DONE
- [ ] **Etapa 2.2** — Parsing de HTML de emails → texto limpo

### Fase 3: Leitura de RSS
- [ ] **Etapa 3.1** — Leitor de feeds RSS/Atom configuráveis
- [ ] **Etapa 3.2** — Normalização: interface unificada para conteúdo (email + RSS)

### Fase 4: Inteligência Artificial
- [ ] **Etapa 4.1** — Integração com OpenAI (resumo de 3 linhas por artigo)
- [ ] **Etapa 4.2** — Geração do ficheiro Markdown diário com template Jinja2

### Fase 5: Automação e Finalização
- [ ] **Etapa 5.1** — Scheduling (execução diária) + entry point robusto
- [ ] **Etapa 5.2** — Testes unitários + documentação final (README)

---

## Tech Stack
- **Linguagem:** Python 3.11+
- **IMAP:** imapclient
- **RSS:** feedparser
- **HTML Parsing:** beautifulsoup4 + html2text
- **IA:** openai (GPT-3.5-turbo)
- **Config:** python-dotenv
- **Templates:** jinja2
- **Scheduling:** schedule
