from fastapi import APIRouter, Depends, HTTPException
from models import Patient
from dependencies import pegar_sessao
from schemas import PatientInput, PatientOutput, PatientQueueInfo
from sqlalchemy.orm import Session
from datetime import datetime
from gemini_service import symptoms_analyze

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
    
    # Count patients ahead by urgency level (only "aguardando" status)
    # Each group only counts patients with lower priority_number (arrived before)
    patients_ahead_high = session.query(Patient).filter(
    Patient.status == "aguardando",
    Patient.urgency_level == "alta",
    Patient.priority_number < patient.priority_number
    ).count()

    patients_ahead_medium = session.query(Patient).filter(
    Patient.status == "aguardando",
    Patient.urgency_level == "média",
    Patient.priority_number < patient.priority_number
    ).count()
    # Medium includes all "alta" patients ahead
    patients_ahead_medium2 = patients_ahead_medium + patients_ahead_high

    patients_ahead_low = session.query(Patient).filter(
    Patient.status == "aguardando",
    Patient.urgency_level == "baixa",
    Patient.priority_number < patient.priority_number
    ).count()
    # Low includes all "alta" and "média" patients ahead
    patients_ahead_low2 = patients_ahead_low + patients_ahead_medium2

    # Calculate estimated waiting time based on urgency level
    # alta: 15 min/patient | média: 10 min/patient | baixa: 5 min/patient
    if(patient.priority_number < 199):
        waiting_time = patients_ahead_high * 15
    elif(200 <= patient.priority_number < 299):
        waiting_time = (patients_ahead_high * 15) + (patients_ahead_medium * 10)
    else:
        waiting_time = (patients_ahead_high * 15) + (patients_ahead_medium * 10) + (patients_ahead_low * 5)  

    # Determine queue position based on urgency level
    if (patient.priority_number < 199):
        queue_position = patients_ahead_high
    elif (200 <= patient.priority_number < 299):
        queue_position = patients_ahead_medium2
    else:
        queue_position = patients_ahead_low2   

    if patient.status != "aguardando":
        raise HTTPException(
        status_code=400,
        detail=f"Paciente não está na fila. Status atual: {patient.status}"
    )

    return PatientQueueInfo(
        patient=patient,
        queue_position=queue_position,
        waiting_time_minutes=waiting_time
    )  