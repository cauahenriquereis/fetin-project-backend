from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

class PatientInput(BaseModel):
   full_name: str
   age: int
   symptoms: str
   pain_level: int

class PatientOutput(BaseModel):
    id: int
    full_name: str
    age: int
    symptoms: str
    pain_level: int
    urgency_level: 
    priority_number:
    status: str
    created_at: datetime

    # Allows Pydantic to read objects returned by SQLAlchemy.
    class Config:
        from_attributes = True

class PatientQueueInfo(BaseModel):
    patient: PatientOutput
    queue_position: int
    waiting_time_minutes: int        

        
class LoginRequest(BaseModel):
    senha: str   

class StatusUpdate(BaseModel):
    # Only accepts valid status values
    new_status: Literal["aguardando", "em atendimento", "atendido"]
