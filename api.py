from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import Session, Clinica, Paciente, Agendamento
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PacienteSchema(BaseModel):
    nome: str
    telefone: str
    cpf: str | None = None
    clinicaId: str

class AgendamentoSchema(BaseModel):
    data: str
    pacienteId: str
    clinicaId: str

@app.get("/pacientes/{clinica_id}")
def listar_pacientes(clinica_id: str):
    db = Session()
    pacientes = db.query(Paciente).filter(Paciente.clinicaId == clinica_id).all()
    db.close()
    return pacientes

@app.post("/pacientes")
def criar_paciente(dados: PacienteSchema):
    db = Session()
    paciente = Paciente(
        id=str(__import__('uuid').uuid4()),
        nome=dados.nome,
        telefone=dados.telefone,
        cpf=dados.cpf,
        clinicaId=dados.clinicaId
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    id_gerado = paciente.id
    db.close()
    return {"mensagem": f"Paciente {dados.nome} cadastrado!", "id": id_gerado}

@app.get("/agendamentos/{clinica_id}")
def listar_agendamentos(clinica_id: str):
    db = Session()
    agendamentos = db.query(Agendamento).filter(Agendamento.clinicaId == clinica_id).all()
    resultado = []
    for a in agendamentos:
        paciente = db.query(Paciente).filter(Paciente.id == a.pacienteId).first()
        resultado.append({
            "id": a.id,
            "data": a.data.isoformat(),
            "status": a.status,
            "paciente": {"nome": paciente.nome if paciente else ""}
        })
    db.close()
    return resultado

@app.post("/agendamentos")
def criar_agendamento(dados: AgendamentoSchema):
    db = Session()
    agendamento = Agendamento(
        id=str(__import__('uuid').uuid4()),
        data=datetime.fromisoformat(dados.data),
        pacienteId=dados.pacienteId,
        clinicaId=dados.clinicaId
    )
    db.add(agendamento)
    db.commit()
    db.close()
    return {"mensagem": "Agendamento criado!"}

@app.get("/agendamentos/{clinica_id}/disponibilidade")
def verificar_disponibilidade(clinica_id: str, data: str):
    db = Session()
    data_dt = datetime.fromisoformat(data)
    agendamento = db.query(Agendamento).filter(
        Agendamento.clinicaId == clinica_id,
        Agendamento.data == data_dt,
        Agendamento.status != "cancelado"
    ).first()
    db.close()
    if agendamento:
        return {"disponivel": False, "mensagem": "Horário já ocupado!"}
    return {"disponivel": True, "mensagem": "Horário disponível!"}

@app.put("/agendamentos/{agendamento_id}/cancelar")
def cancelar_agendamento(agendamento_id: str):
    db = Session()
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not agendamento:
        db.close()
        return {"erro": "Agendamento não encontrado"}
    agendamento.status = "cancelado"
    db.commit()
    db.close()
    return {"mensagem": "Agendamento cancelado com sucesso!"}