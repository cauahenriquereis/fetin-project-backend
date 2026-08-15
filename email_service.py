import resend
from config import RESEND_API_KEY

resend.api_key = RESEND_API_KEY

def send_queue_update_email(patient_name: str, patient_email: str, queue_position: int, waiting_time: int):
    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": patient_email,
            "subject": "Atualização da sua posição na fila — TriagemIA",
            "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #00526d;">TriagemIA — Atualização de Fila</h2>
                    <p>Olá, <strong>{patient_name}</strong>!</p>
                    <p>Sua posição na fila foi atualizada:</p>
                    <div style="background-color: #ebf1f9; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <p style="font-size: 18px;">📍 Posição na fila: <strong>{queue_position}º</strong></p>
                        <p style="font-size: 18px;">⏱ Tempo estimado de espera: <strong>~ {waiting_time} minutos</strong></p>
                    </div>
                    <p style="color: #666;">Por favor, mantenha-se disponível e recomendamos que chegue ao hospital com antecedência.</p>
                    <p style="color: #00526d; font-weight: bold;">TriagemIA — Sistema de Triagem Inteligente</p>
                </div>
            """
        })
    except Exception as e:
        print(f"Erro ao enviar email para {patient_email}: {e}")