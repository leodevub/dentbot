from sqlalchemy import create_engine, Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uuid

DATABASE_URL = "sqlite:///dentsec.db"

engine = create_engine(DATABASE_URL)
Base = declarative_base()

def gerar_id():
    return str(uuid.uuid4())

class Clinica(Base):
    __tablename__ = "clinicas"
    id       = Column(String, primary_key=True, default=gerar_id)
    nome     = Column(String)
    telefone = Column(String, nullable=True)
    email    = Column(String, unique=True)
    pacientes    = relationship("Paciente", back_populates="clinica")
    agendamentos = relationship("Agendamento", back_populates="clinica")

class Paciente(Base):
    __tablename__ = "pacientes"
    id        = Column(String, primary_key=True, default=gerar_id)
    nome      = Column(String)
    telefone  = Column(String)
    cpf       = Column(String, nullable=True)
    clinicaId = Column(String, ForeignKey("clinicas.id"))
    clinica      = relationship("Clinica", back_populates="pacientes")
    agendamentos = relationship("Agendamento", back_populates="paciente")

class Agendamento(Base):
    __tablename__ = "agendamentos"
    id              = Column(String, primary_key=True, default=gerar_id)
    data            = Column(DateTime)
    status          = Column(String, default="pendente")
    lembreteEnviado = Column(Boolean, default=False)
    pacienteId      = Column(String, ForeignKey("pacientes.id"))
    clinicaId       = Column(String, ForeignKey("clinicas.id"))
    paciente = relationship("Paciente", back_populates="agendamentos")
    clinica  = relationship("Clinica", back_populates="agendamentos")

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)