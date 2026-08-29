from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class PatientInput(BaseModel):
   full_name: str
   email: str | None = None
   age: int
   symptoms: str
   pain_level: int

class PatientOutput(BaseModel):
    id: int
    full_name: str
    email: str | None = None
    age: int
    symptoms: str
    pain_level: int
    urgency_level: str | None = None
    priority_number: int | None = None
    status: str
    created_at: datetime
    temperature: float | None = None
    systolic_pressure: int | None = None
    diastolic_pressure: int | None = None
    heart_rate: int | None = None
    oxygen_saturation: int | None = None

    class Config:
        from_attributes = True

class PatientQueueInfo(BaseModel):
    patient: PatientOutput
    queue_position: int
    waiting_time_minutes: int   
    priority_number: int     

class TriageResponse(BaseModel):
    urgency_level: Literal["baixa", "média", "alta"] = Field(
        description="Nível de urgência estrito."
    )

class LoginRequest(BaseModel):
    senha: str   

class StatusUpdate(BaseModel):
    new_status: Literal["aguardando", "em atendimento", "atendido"]

class VitalSignsInput(BaseModel):
    temperature: float = Field(ge=30.0, le=43.0)
    systolic_pressure: int = Field(ge=60, le=250)
    diastolic_pressure: int = Field(ge=30, le=150)
    heart_rate: int = Field(ge=30, le=220)
    oxygen_saturation: int = Field(ge=50, le=100)
