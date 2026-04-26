Não tem! Vamos criar. Cola isso no arquivo README.md dentro da pasta do dentbot e sobe no GitHub:
markdown# 🦷 DentBot — Sistema de Agendamento Odontológico

Bot de agendamento de consultas odontológicas com IA integrada, desenvolvido do zero e em uso real por uma clínica odontológica.

🔗 **[Acessar o Bot](https://t.me/Dentist_cbot)**

## ✨ Funcionalidades

- 📅 Agendamento de consultas com verificação de disponibilidade em tempo real
- ❌ Cancelamento de consultas
- 📋 Listagem de consultas agendadas
- 🔐 Painel administrativo com senha para a clínica
- 🤖 Respostas dinâmicas com IA via LLaMA/Groq
- 💬 Botões interativos inline

## 🏗️ Arquitetura
Paciente → Telegram → Bot (Python) → API (FastAPI) → Banco (SQLAlchemy/SQLite)
↘ IA (Groq/LLaMA)

## 🛠️ Tecnologias

- **Python** — linguagem principal
- **FastAPI** — API REST
- **SQLAlchemy** — banco de dados ORM
- **SQLite** — armazenamento dos dados
- **python-telegram-bot** — integração com Telegram
- **Groq/LLaMA** — IA para respostas dinâmicas
- **Railway** — deploy em produção 24h
- **httpx** — requisições HTTP assíncronas

## 🚀 Como rodar localmente

1. Instala as dependências:
pip install fastapi uvicorn sqlalchemy httpx python-telegram-bot

2. Configura a variável de ambiente:
export TOKEN=seu-token-do-botfather

3. Roda a API:
python -m uvicorn api:app --reload

4. Roda o bot:
python bot.py

## 📁 Estrutura
dentbot/
├── api.py          # API REST com FastAPI
├── bot.py          # Bot do Telegram
├── database.py     # Models do banco de dados
└── README.md

## 👨‍💻 Autor

**Leonardo Duarte de Abreu**  
[github.com/leodevub](https://github.com/leodevub) · [linkedin.com/in/leonardo-duarte-166a3b26a](https://linkedin.com/in/leonardo-duarte-166a3b26a)

---

*Sistema em uso real por clínica odontológica*
