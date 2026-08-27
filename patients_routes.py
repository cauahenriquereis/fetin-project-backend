from fastapi import APIRouter, Depends, HTTPException
from models import Patient
from dependencies import pegar_sessao
from schemas import PatientInput, PatientOutput, PatientQueueInfo
from sqlalchemy.orm import Session
from datetime import datetime
from gemini_service import symptoms_analyze
from queue_routes import calculate_queue_info
from email_service import send_queue_update_email
from queue_routes import get_calc_fn

patient_router = APIRouter(prefix="/patients", tags = ["patients"])

@patient_router.get("/")
async def home():
    return{"mensagem": "Você acessou a rota padrão de pacientes", "autenticado":False}

@patient_router.post("/register", response_model = PatientOutput)
async def register_patient(patient_input: PatientInput, session: Session = Depends(pegar_sessao)):

    analyze = await symptoms_analyze(patient_input.symptoms, patient_input.pain_level, patient_input.age)
    urgency_level = analyze["urgency_level"]

    urgency_order = {"alta": 1, "média": 2, "baixa": 3}
    urgency_weight = urgency_order.get(urgency_level, 2)

    last_patient = session.query(Patient).filter(
    Patient.status == "aguardando",
    Patient.urgency_level == urgency_level
    ).order_by(Patient.priority_number.desc()).first()

    if last_patient:
        if last_patient.priority_number == 199 or last_patient.priority_number == 299:
            priority_number = urgency_weight * 100
        else:    
            priority_number = last_patient.priority_number + 1
    else:
        priority_number = urgency_weight * 100

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

    if new_patient.email:
        queue_position, waiting_time = calculate_queue_info(new_patient, session)
        send_queue_update_email(new_patient.full_name, new_patient.email, queue_position, waiting_time)

    return new_patient

@patient_router.get("/{patient_id}", response_model = PatientQueueInfo)
async def get_patient(
    patient_id: int, 
    session: Session = Depends(pegar_sessao),
    calc_fn = Depends(get_calc_fn),
    ):
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    if patient.status != "aguardando":
        raise HTTPException(
        status_code=400,
        detail=f"Paciente não está na fila. Status atual: {patient.status}"
    )

    queue_position, waiting_time = calc_fn(patient, session)
    
    return PatientQueueInfo(
        patient=patient,
        queue_position=queue_position,
        waiting_time_minutes=waiting_time,
        priority_number=patient.priority_number
    )  