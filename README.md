# DentBot 🦷

Bot de agendamento de consultas odontológicas integrado com banco de dados em tempo real.

## O que faz

- Paciente manda mensagem no Telegram
- Bot verifica disponibilidade do horário
- Agenda a consulta automaticamente
- Confirma com data em português

## Tecnologias

- Python
- FastAPI — API REST
- SQLAlchemy — banco de dados
- python-telegram-bot — integração com Telegram
- SQLite — armazenamento dos dados

## Como rodar

1. Clone o repositório
2. Instale as dependências:
   pip install -r requirements.txt
3. Rode a API:
   python -m uvicorn api:app --reload
4. Rode o bot:
   python bot.py

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /pacientes/{clinica_id} | Lista pacientes |
| POST | /pacientes | Cadastra paciente |
| GET | /agendamentos/{clinica_id} | Lista agendamentos |
| POST | /agendamentos | Cria agendamento |
| GET | /agendamentos/{clinica_id}/disponibilidade | Verifica horário |

## Projeto real

Desenvolvido para uso em clínica odontológica real.
