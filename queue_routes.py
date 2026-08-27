from fastapi import APIRouter, Depends, HTTPException
from dependencies import verify_token
from dependencies import pegar_sessao
from sqlalchemy.orm import Session
from models import Patient
from schemas import PatientOutput, StatusUpdate
from typing import List
from email_service import send_queue_update_email

def calculate_queue_info(patient: Patient, session: Session):
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
    patients_ahead_medium2 = patients_ahead_medium + patients_ahead_high

    patients_ahead_low = session.query(Patient).filter(
        Patient.status == "aguardando",
        Patient.urgency_level == "baixa",
        Patient.priority_number < patient.priority_number
    ).count()
    patients_ahead_low2 = patients_ahead_low + patients_ahead_medium2

    if patient.priority_number <= 199:
        queue_position = patients_ahead_high + 1
    elif 200 <= patient.priority_number <= 299:
        queue_position = patients_ahead_medium2 + 1
    else:
        queue_position = patients_ahead_low2 + 1

    if patient.priority_number <= 199:
        waiting_time = patients_ahead_high * 10
    elif 200 <= patient.priority_number <= 299:
        waiting_time = (patients_ahead_high * 10) + (patients_ahead_medium * 7)
    else:
        waiting_time = (patients_ahead_high * 10) + (patients_ahead_medium * 7) + (patients_ahead_low * 5)

    return queue_position, waiting_time

# All routes require a valid JWT token — doctor access only
queue_router = APIRouter(prefix="/queue", tags = ["queue"], dependencies=[Depends(verify_token)])

@queue_router.get("/")
async def home():
    return{"mensagem": "Você acessou a rota padrão de filas", "autenticado":True}

@queue_router.get("/status", response_model = List[PatientOutput])
async def get_ordered_queue(session :Session = Depends(pegar_sessao)):
    patients = session.query(Patient).filter(Patient.status == "aguardando").order_by(Patient.priority_number).all()   
    return patients

@queue_router.get("/next/", response_model = PatientOutput)
async def get_next_patient(session :Session = Depends(pegar_sessao)):
    patient = session.query(Patient).filter(Patient.status == "aguardando").order_by(Patient.priority_number).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Não há pacientes aguardando atendimento")
    return patient

@queue_router.get("/status/{patient_id}", response_model = PatientOutput)
async def get_patient_status(patient_id: int, session :Session = Depends(pegar_sessao)):
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return patient

@queue_router.patch("/{patient_id}/status", response_model = PatientOutput)
async def update_patient_status(patient_id: int, dados: StatusUpdate, session :Session = Depends(pegar_sessao)):
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    patient.status = dados.new_status
    session.commit()
    session.refresh(patient)

    if dados.new_status == "atendido":
        waiting_patients_with_email = session.query(Patient).filter(
        Patient.status == "aguardando",
        Patient.email != None
        ).all()

        for p in waiting_patients_with_email:
            queue_position, waiting_time = calculate_queue_info(p, session)
            send_queue_update_email(p.full_name, p.email, queue_position, waiting_time)
    return patient

@queue_router.delete("/{patient_id}")
async def remove_patient_from_queue(patient_id: int, session :Session = Depends(pegar_sessao)):
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    session.delete(patient)
    session.commit()
    return {"mensagem": f"Paciente {patient.full_name} removido da fila"}

    