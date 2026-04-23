from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import httpx
from datetime import datetime

API_URL = "http://dentbot-production.up.railway.app"
CLINICA_ID = "b5e74e86-e9c5-4547-a0b4-e1dcd207280d"
SENHA_ADMIN = "dentsec2026"

meses = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
         "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

def formatar_data(data_dt):
    return f"{data_dt.day} de {meses[data_dt.month-1]} de {data_dt.year} às {data_dt.strftime('%H:%M')}"

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Agendar consulta", callback_data="agendar")],
        [InlineKeyboardButton("📋 Ver consultas", callback_data="consultas")],
        [InlineKeyboardButton("❌ Cancelar consulta", callback_data="cancelar")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! Bem-vindo à Clínica DentSec! 🦷\n\nComo posso te ajudar?",
        reply_markup=menu()
    )

async def consultas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient() as client:
        resposta = await client.get(f"{API_URL}/agendamentos/{CLINICA_ID}")
        agendamentos = resposta.json()
    if not agendamentos:
        await update.message.reply_text("Nenhuma consulta agendada.")
        return
    texto = "Consultas agendadas:\n\n"
    for a in agendamentos:
        data_dt = datetime.fromisoformat(a["data"])
        texto += f"{formatar_data(data_dt)} — Status: {a['status']}\n"
    await update.message.reply_text(texto)

async def botao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "agendar":
        context.user_data["etapa"] = "nome"
        context.user_data["dados"] = {}
        await query.message.reply_text("Vamos agendar sua consulta!\n\nQual é o seu nome?")

    elif query.data == "consultas":
        async with httpx.AsyncClient() as client:
            resposta = await client.get(f"{API_URL}/agendamentos/{CLINICA_ID}")
            agendamentos = resposta.json()
        if not agendamentos:
            await query.message.reply_text("Nenhuma consulta agendada.")
            return
        texto = "Consultas agendadas:\n\n"
        for a in agendamentos:
            data_dt = datetime.fromisoformat(a["data"])
            texto += f"{formatar_data(data_dt)} — Status: {a['status']}\n"
        await query.message.reply_text(texto)

    elif query.data == "cancelar":
        context.user_data["etapa"] = "cancelar"
        await query.message.reply_text(
            "Para cancelar me informe:\n"
            "Seu nome e a data\n\n"
            "Exemplo: Leonardo, 25/04/2026 11:00"
        )

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    etapa = context.user_data.get("etapa")
    dados = context.user_data.get("dados", {})
    texto = update.message.text.strip()

    if etapa == "admin_senha":
        if texto == SENHA_ADMIN:
            context.user_data["etapa"] = None
        async with httpx.AsyncClient() as client:
            resposta = await client.get(f"{API_URL}/agendamentos/{CLINICA_ID}")
            agendamentos = resposta.json()
        
        if not agendamentos:
            await update.message.reply_text("Nenhum agendamento encontrado.")
            return
        
        texto_admin = "📋 Todos os agendamentos:\n\n"
        for a in agendamentos:
            data_dt = datetime.fromisoformat(a["data"])
            texto_admin += (
                f"👤 {a['paciente']['nome']}\n"
                f"📅 {formatar_data(data_dt)}\n"
                f"Status: {a['status']}\n"
                f"─────────────\n"
            )
        await update.message.reply_text(texto_admin)
    else:
        context.user_data["etapa"] = None
        await update.message.reply_text("Senha incorreta!")
    if etapa == "nome":
        dados["nome"] = texto
        context.user_data["dados"] = dados
        context.user_data["etapa"] = "telefone"
        await update.message.reply_text("Qual é o seu telefone?")
        

    elif etapa == "telefone":
        dados["telefone"] = texto
        context.user_data["dados"] = dados
        context.user_data["etapa"] = "data"
        await update.message.reply_text(
            "Qual data e horário deseja?\n\n"
            "Exemplo: 25/04/2026 14:00"
        )

    elif etapa == "data":
        try:
            data_dt = datetime.strptime(texto, "%d/%m/%Y %H:%M")
            if data_dt < datetime.now():
                await update.message.reply_text("Não é possível agendar no passado! Escolha outra data.")
                return
            dados["data"] = texto
            dados["data_dt"] = data_dt.isoformat()
            context.user_data["dados"] = dados
            context.user_data["etapa"] = "confirmacao"
            await update.message.reply_text(
                f"Confirma o agendamento?\n\n"
                f"Nome: {dados['nome']}\n"
                f"Telefone: {dados['telefone']}\n"
                f"Data: {formatar_data(data_dt)}\n\n"
                f"Responda sim ou não"
            )
        except:
            await update.message.reply_text("Formato inválido! Use: 25/04/2026 14:00")

    elif etapa == "confirmacao":
        if texto.lower() == "sim":
            try:
                async with httpx.AsyncClient() as client:
                    disp = await client.get(
                        f"{API_URL}/agendamentos/{CLINICA_ID}/disponibilidade",
                        params={"data": dados["data_dt"]}
                    )
                    if not disp.json()["disponivel"]:
                        context.user_data["etapa"] = "data"
                        await update.message.reply_text("Horário indisponível! Escolha outra data e horário:")
                        return
                    pac = await client.post(f"{API_URL}/pacientes", json={
                        "nome": dados["nome"],
                        "telefone": dados["telefone"],
                        "clinicaId": CLINICA_ID
                    })
                    paciente_id = pac.json().get("id")
                    await client.post(f"{API_URL}/agendamentos", json={
                        "data": dados["data_dt"],
                        "pacienteId": paciente_id,
                        "clinicaId": CLINICA_ID
                    })
                context.user_data["etapa"] = None
                context.user_data["dados"] = {}
                data_dt = datetime.fromisoformat(dados["data_dt"])
                await update.message.reply_text(
                    f"Consulta agendada com sucesso!\n\n"
                    f"Nome: {dados['nome']}\n"
                    f"Data: {formatar_data(data_dt)}\n\n"
                    f"Até logo! 😊",
                    reply_markup=menu()
                )
            except Exception as e:
                print("Erro:", e)
                await update.message.reply_text("Erro ao agendar. Tente novamente.")
        elif texto.lower() in ["não", "nao"]:
            context.user_data["etapa"] = None
            context.user_data["dados"] = {}
            await update.message.reply_text("Agendamento cancelado.", reply_markup=menu())
        else:
            await update.message.reply_text("Responda apenas sim ou não.")

    elif etapa == "cancelar":
        try:
            partes = texto.split(",")
            nome = partes[0].strip()
            data_str = partes[1].strip()
            data_dt = datetime.strptime(data_str, "%d/%m/%Y %H:%M")
            async with httpx.AsyncClient() as client:
                resposta = await client.get(f"{API_URL}/agendamentos/{CLINICA_ID}")
                todos = resposta.json()
            encontrado = None
            for a in todos:
                data_a = datetime.fromisoformat(a["data"])
                if a["paciente"]["nome"].lower() == nome.lower() and data_a == data_dt:
                    encontrado = a
                    break
            if not encontrado:
                await update.message.reply_text("Consulta não encontrada. Verifique o nome e a data.")
                return
            async with httpx.AsyncClient() as client:
                await client.put(f"{API_URL}/agendamentos/{encontrado['id']}/cancelar")
            context.user_data["etapa"] = None
            await update.message.reply_text("Consulta cancelada com sucesso! ✅", reply_markup=menu())
        except Exception as e:
            print("Erro:", e)
            await update.message.reply_text("Formato inválido! Use:\nNome, 25/04/2026 11:00")

    else:
        await update.message.reply_text("Use o menu abaixo:", reply_markup=menu())


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["etapa"] = "admin_senha"
    await update.message.reply_text("Digite a senha de administrador:") 

    async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
     print("Admin chamado!")
    context.user_data["etapa"] = "admin_senha"
    await update.message.reply_text("Digite a senha de administrador:")      

app = ApplicationBuilder().token("8766237462:AAFC6rhf6qJoWGlenrlqMbMHRz2uCWmp9lk").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CallbackQueryHandler(botao))
app.add_handler(MessageHandler(filters.TEXT, responder))

print("Bot rodando...")
app.run_polling()