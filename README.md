# 📰 EasyNewsletter

**Agregador de Newsletter Pessoal no Terminal / Markdown**

Transforma o caos da tua caixa de entrada num jornal diário limpo e elegante em Markdown.

## O que faz

1. Liga-se ao teu email (IMAP) ou lê feeds RSS dos teus sites favoritos
2. Extrai o texto limpo dos artigos (remove HTML, ads, tracking)
3. Usa IA para gerar um **resumo de 3 linhas** de cada artigo
4. Cria um ficheiro `.md` diário — o teu jornal privado no VS Code

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

## Configuração

Copia `.env.example` para `.env` e preenche:

- `EMAIL_ADDRESS` — O teu email
- `EMAIL_PASSWORD` — App Password do Gmail (não a password normal!)
- `OPENAI_API_KEY` — Chave da API OpenAI

> ⚠️ **Gmail:** Usa uma [App Password](https://myaccount.google.com/apppasswords), não a password da conta.

## Output

Os digestos diários são gerados em `output/` com o formato:
```
output/digest_2026-06-20.md
```
