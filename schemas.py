from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class PatientInput(BaseModel):
   full_name: str
   email: str
   age: int
   symptoms: str
   pain_level: int

class PatientOutput(BaseModel):
    id: int
    full_name: str
    email: str
    age: int
    symptoms: str
    pain_level: int
    urgency_level: str
    priority_number: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class PatientQueueInfo(BaseModel):
    patient: PatientOutput
    queue_position: int
    waiting_time_minutes: int   
    priority_number: int     

class LoginRequest(BaseModel):
    senha: str   

class StatusUpdate(BaseModel):
    new_status: Literal["aguardando", "em atendimento", "atendido"]
