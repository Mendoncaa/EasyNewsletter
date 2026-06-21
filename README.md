# 📰 EasyNewsletter

**Agregador de Newsletter Pessoal no Terminal / Markdown**

Transforma o caos da tua caixa de entrada num jornal diário limpo e elegante em Markdown.

## O que faz

1. Liga-se ao teu email (IMAP) ou lê feeds RSS dos teus sites favoritos
2. Extrai o texto limpo dos artigos (remove HTML, ads, tracking pixels)
3. Usa IA para gerar um **resumo de 3 linhas** de cada artigo (ou fallback inteligente)
4. Cria um ficheiro `.md` diário — o teu jornal privado no VS Code

## Arquitetura

```
src/
├── config.py              # Gestão de configuração via .env
├── email_reader.py        # Conexão IMAP + fetch de emails
├── rss_reader.py          # Leitura de feeds RSS/Atom
├── html_parser.py         # Limpeza HTML → texto (BS4 + html2text)
├── summarizer.py          # Resumos via OpenAI ou fallback
├── aggregator.py          # Interface unificada email + RSS
└── markdown_generator.py  # Geração do digest .md com Jinja2
```

## Setup Rápido

```bash
# 1. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar credenciais
copy .env.example .env
# Editar .env com as tuas credenciais

# 4. Executar
python main.py
```

## Uso

```bash
# Gerar digest de hoje (últimas 24h)
python main.py

# Gerar digest dos últimos 3 dias
python main.py --days 3

# Modo agendado: executa todos os dias às 07:00
python main.py --schedule

# Modo agendado com hora personalizada
python main.py --schedule --time 08:30
```

## Configuração

Copia `.env.example` para `.env` e preenche:

- `EMAIL_ADDRESS` — O teu email
- `EMAIL_PASSWORD` — App Password do Gmail (não a password normal!)
- `OPENAI_API_KEY` — Chave da API OpenAI (opcional — há fallback)
- `RSS_FEEDS` — URLs de feeds RSS separados por vírgula

> ⚠️ **Gmail:** Usa uma [App Password](https://myaccount.google.com/apppasswords), não a password da conta.

## Testes

```bash
python -m pytest tests/ -v
```

## Output

Os digestos diários são gerados em `output/` com o formato:
```
output/digest_2026-06-20.md
```
