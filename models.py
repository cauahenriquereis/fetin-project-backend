from sqlalchemy import create_engine, Column,String,Integer,DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# Creates the connection engine to the Neon PostgreSQL database
# pool_pre_ping=True checks if connection is alive before using it
db = create_engine(os.getenv("DATABASE_URL"),  pool_pre_ping=True)

#create the base of the database
Base = declarative_base()

#create the classes/tables of the database

class Patient(Base):
    __tablename__ = "patients"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    full_name = Column("full_name", String(100), nullable=False)
    email = Column("email", String(100), nullable=True)
    age = Column("age", Integer, nullable=False)
    symptoms = Column("symptoms", Text, nullable=False)
    pain_level = Column("pain_level", Integer, nullable=False)   
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

# Create tables if they don't exist
Base.metadata.create_all(db)