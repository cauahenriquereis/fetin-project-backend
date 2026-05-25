import json
import time
from pydantic import BaseModel, Field
from typing import Literal
from google import genai
from google.genai import types, errors as genai_errors
from config import GEMINI_API_KEY

# Initialize Gemini client once at module level
client = genai.Client(api_key=GEMINI_API_KEY)


class TriageResponse(BaseModel):
    urgency_level: Literal["baixa", "média", "alta"] = Field(
        description="Nível de urgência estrito."
    )
    reasoning: str = Field(
        description="Explicação clínica direta, técnica e em terceira pessoa (máx. 2 frases)."
    )

def symptoms_analyze(symptoms: str, pain_level: int, age: int) -> dict:
    system_instruction = """Você é a IA médica de triagem do sistema hospitalar FETIN, atuando com base em diretrizes rigorosas (semelhantes ao Protocolo de Manchester adaptado para 3 níveis). Sua função é classificar pacientes de forma segura e analítica, focando no risco de morbimortalidade.

DIRETRIZES DE TRIAGEM CLÍNICA:
1. Peso da Dor vs. Quadro Clínico: A dor é subjetiva. Uma dor 10/10 com sintomas de resfriado leve ou dor crônica continua sendo urgência "baixa". Sempre priorize os sinais vitais presumidos e a natureza dos sintomas descritos.
2. Fator Etário (Vulnerabilidade): Pacientes nos extremos de idade (menores de 5 anos ou maiores de 65 anos) possuem menor reserva fisiológica. Sintomas moderados nessas faixas etárias devem ter sua gravidade elevada.
3. Critérios para "alta": Risco de vida imediato ou perda de membro. (ex: dor torácica irradiada, dificuldade respiratória severa, sinais de AVC, sangramento incontrolável).
4. Critérios para "média": Condições agudas que necessitam de avaliação médica rápida, sem risco de morte iminente. (ex: fraturas fechadas, dor abdominal aguda, cortes profundos).
5. Critérios para "baixa": Condições crônicas agudizadas, quadros não-urgentes ou queixas leves. (ex: sintomas de vias aéreas superiores, dores musculares sem trauma)."""

    user_prompt = f"""
DADOS DO PACIENTE:
- Idade: {age} anos
- Sintomas relatados: {symptoms}
- Dor autorrelatada: {pain_level}/10
"""

    max_tentativas = 3
    for tentativa in range(1, max_tentativas + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction, 
                    temperature=0.0, 
                    response_mime_type="application/json",
                    response_schema=TriageResponse, 
                )
            )

            resultado = json.loads(response.text)
            resultado["ai_analyzed"] = True
            
            return resultado

        except genai_errors.ServerError as e:
            print(f"Tentativa {tentativa}/{max_tentativas} falhou por erro de servidor: {e}")
            if tentativa < max_tentativas:
                time.sleep(2) 
            else:
                return {"urgency_level": "média", "reasoning": "Serviço temporariamente indisponível", "ai_analyzed": False}

        except genai_errors.ClientError as e:
            print(f"Erro na API do Gemini (Client/Auth): {e}")
            return {"urgency_level": "média", "reasoning": "Erro na análise automática (Client)", "ai_analyzed": False}

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Erro no processamento da resposta da IA: {e}")
            return {"urgency_level": "média", "reasoning": "Erro na formatação ou conteúdo bloqueado", "ai_analyzed": False}