import asyncio
import json
from google import genai
from google.genai import types, errors as genai_errors
from config import GEMINI_API_KEY
from schemas import TriageResponse

client = genai.Client(api_key=GEMINI_API_KEY)

async def symptoms_analyze(
    symptoms: str, 
    pain_level: int, 
    age: int, 
    temperature: float, 
    systolic_pressure: int, 
    diastolic_pressure: int, 
    heart_rate: int, 
    oxygen_saturation: int
) -> dict:
    
    system_instruction = """Você é a IA médica de triagem do sistema hospitalar FETIN, atuando com base em diretrizes rigorosas (semelhantes ao Protocolo de Manchester adaptado para 3 níveis de gravidade: Alta, Média e Baixa). Sua função é classificar pacientes de forma segura e analítica, focando no risco de morbimortalidade e na estabilidade hemodinâmica.

DIRETRIZES DE TRIAGEM CLÍNICA:

1. Avaliação de Sinais Vitais e Parâmetros Fisiológicos:
   - Saturação de Oxigênio (SpO2):
     * SpO2 < 92% (ou < 90% em DPOC): Critério imediato para urgência "alta" (risco de hipóxia severa).
     * SpO2 entre 92% e 94%: Requer atenção, geralmente urgência "média" ou "alta" se associado à dispneia.
   - Frequência Cardíaca (FC):
     * FC > 120 bpm (taquicardia severa) ou FC < 50 bpm (bradicardia severa) em repouso: Eleva a classificação para "alta" ou "média" dependendo do quadro geral.
   - Pressão Arterial (PA):
     * Crise Hipertensiva (Sistólica ≥ 180 mmHg ou Diastólica ≥ 110 mmHg) com sintomas associados (cefaleia intensa, visão turva, dor torácica): Urgência "alta".
     * Hipotensão (Sistólica < 90 mmHg): Sinal de choque/sepse, classificar como urgência "alta".
   - Temperatura Corporal:
     * Hipertermia extrema (≥ 39.5 ºC) ou Hipotermia (< 35 ºC): Requer urgência "alta" ou "média" (especialmente em idosos/bebês).
     * Febre moderada (37.8 ºC a 39.4 ºC): Geralmente urgência "média" ou "baixa", dependendo dos sintomas acompanhantes.

2. Peso da Dor vs. Quadro Clínico: A dor é um sintoma subjetivo. Uma dor 10/10 com sinais vitais estáveis e sintomas de resfriado leve ou dor crônica sem trauma continua sendo urgência "baixa". Sempre correlacione o nível de dor com a alteração dos sinais vitais e o risco fisiológico real.

3. Fator Etário (Vulnerabilidade): Pacientes nos extremos de idade (menores de 5 anos ou maiores de 65 anos) possuem menor reserva fisiológica e apresentação atípica de sintomas. Qualquer alteração moderada em sinais vitais nessas faixas etárias deve elevar a gravidade (ex: febre em lactente ou idoso confuso é urgência "alta" ou "média").

4. Critérios para Urgência ALTA (Vermelho/Laranja adaptado):
   - Risco de vida imediato, alteração grave de sinais vitais ou risco de perda de membro/função.
   - Exemplos: Dor torácica com irradiação, dispneia severa, rebaixamento do nível de consciência, sinais de AVC, sangramento incontrolável, Anafilaxia, SpO2 < 92%, PA Sistólica < 90 mmHg ou ≥ 180 mmHg sintomática.

5. Critérios para Urgência MÉDIA (Amarelo adaptado):
   - Condições agudas que necessitam de avaliação médica rápida, sem risco de morte iminente, mas com potencial de deterioração.
   - Exemplos: Fraturas fechadas, dor abdominal aguda moderada/intensa, cortes profundos necessitando de sutura, febre alta isolada, vômitos persistentes com risco de desidratação, sinais vitais levemente alterados.

6. Critérios para Urgência BAIXA (Verde/Azul adaptado):
   - Condições crônicas agudizadas sem gravidade, quadros não-urgentes ou queixas leves com sinais vitais dentro da normalidade.
   - Exemplos: Sintomas de vias aéreas superiores (coriza, dor de garganta leve), dores musculares sem trauma, renovação de receitas, trocas de curativo, dores crônicas sem alteração de padrão."""

    user_prompt = f"""
DADOS DO PACIENTE PARA TRIAGEM:
- Idade: {age} anos
- Sintomas relatados: {symptoms}
- Dor autorrelatada: {pain_level}/10
- Temperatura Corporal: {temperature} ºC
- Pressão Arterial: {systolic_pressure}/{diastolic_pressure} mmHg
- Frequência Cardíaca: {heart_rate} bpm
- Saturação de Oxigênio (SpO2): {oxygen_saturation} %
"""

    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            response = await client.aio.models.generate_content(
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
            
            return resultado

        except genai_errors.ServerError as e:
            if tentativa < max_tentativas - 1:
                await asyncio.sleep(2)
            else:
                return {"urgency_level": "média"}

        except genai_errors.ClientError as e:
            return {"urgency_level": "média"}

        except (json.JSONDecodeError, ValueError) as e:
            return {"urgency_level": "média"}