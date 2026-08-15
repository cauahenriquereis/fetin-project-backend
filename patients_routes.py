from fastapi import APIRouter, Depends, HTTPException
from models import Patient
from dependencies import pegar_sessao
from schemas import PatientInput, PatientOutput, PatientQueueInfo
from sqlalchemy.orm import Session
from datetime import datetime
from gemini_service import symptoms_analyze
from queue_routes import calculate_queue_info

# Public router — no authentication required (accessed by patients at the totem)
patient_router = APIRouter(prefix="/patients", tags = ["patients"])

@patient_router.get("/")
async def home():
    return{"mensagem": "Você acessou a rota padrão de pacientes", "autenticado":False}

@patient_router.post("/register", response_model = PatientOutput)
async def register_patient(patient_input: PatientInput, session: Session = Depends(pegar_sessao)):

    # Step 1: Analyze symptoms with Gemini AI
    analyze = symptoms_analyze(patient_input.symptoms, patient_input.pain_level, patient_input.age)
    urgency_level = analyze["urgency_level"]

    # Step 2: Map urgency level to numeric weight (lower = higher priority)
    urgency_order = {"alta": 1, "média": 2, "baixa": 3}
    urgency_weight = urgency_order.get(urgency_level, 2)

    # Step 3: Calculate priority number based on last patient with same urgency
    # Avoids duplicate priority numbers when patients are removed from queue
    last_patient = session.query(Patient).filter(
    Patient.status == "aguardando",
    Patient.urgency_level == urgency_level
    ).order_by(Patient.priority_number.desc()).first()

    if last_patient:
        priority_number = last_patient.priority_number + 1
    else:
        priority_number = urgency_weight * 100

    print(f"AI analyzed: {analyze['ai_analyzed']}")

    # Step 4: Save patient to database
    new_patient = Patient(
        full_name=patient_input.full_name,
        email=patient_input.email,
        age=patient_input.age,
        symptoms=patient_input.symptoms,
        pain_level=patient_input.pain_level,
        urgency_level = urgency_level,
        priority_number = priority_number,
        status="aguardando",
        created_at=datetime.now()
    )

    session.add(new_patient)
    session.commit()
    session.refresh(new_patient) 
    return new_patient

@patient_router.get("/{patient_id}", response_model = PatientQueueInfo)
async def get_patient(patient_id: int, session: Session = Depends(pegar_sessao)):
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    if patient.status != "aguardando":
        raise HTTPException(
        status_code=400,
        detail=f"Paciente não está na fila. Status atual: {patient.status}"
    )

    # Calculate queue position and waiting time
    queue_position, waiting_time = calculate_queue_info(patient, session)
    
    return PatientQueueInfo(
        patient=patient,
        queue_position=queue_position,
        waiting_time_minutes=waiting_time,
        priority_number=patient.priority_number
    )  