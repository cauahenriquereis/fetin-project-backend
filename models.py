from sqlalchemy import create_engine, Column,String,Integer,DateTime, Enum, Text, Float
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
from config import DATABASE_URL
import os

db = create_engine(DATABASE_URL,  pool_pre_ping=True)

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    full_name = Column("full_name", String(100), nullable=False)
    email = Column("email", String(100), nullable=True)
    age = Column("age", Integer, nullable=False)
    symptoms = Column("symptoms", Text, nullable=False)
    pain_level = Column("pain_level", Integer, nullable=False)  
    temperature = Column("temperature", Float, nullable=True) 
    systolic_pressure = Column("systolic_pressure", Integer, nullable=True)
    diastolic_pressure = Column("diastolic_pressure", Integer, nullable=True)
    heart_rate = Column("heart_rate", Integer, nullable=True)
    oxygen_saturation = Column("oxygen_saturation", Integer, nullable=True)
    urgency_level = Column("urgency_level", Enum("baixa", "média", "alta", name="urgency_level_enum"))
    priority_number = Column("priority_number", Integer)
    status = Column("status", Enum("aguardando", "em atendimento", "atendido", name="patient_status_enum"), nullable=False)
    created_at = Column("created_at", DateTime, nullable=False)

    def __init__ (self, full_name, email, age, symptoms, pain_level, urgency_level, priority_number, status, created_at):
        self.full_name = full_name
        self.email = email
        self.age = age
        self.symptoms = symptoms
        self.pain_level = pain_level
        self.urgency_level = urgency_level
        self.priority_number = priority_number
        self.status = status
        self.created_at = created_at

Base.metadata.create_all(db)