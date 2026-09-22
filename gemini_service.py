import asyncio
import json
from typing import Optional
from google import genai
from google.genai import types, errors as genai_errors
from config import GEMINI_API_KEY
from schemas import TriageResponse

client = genai.Client(api_key=GEMINI_API_KEY)

async def symptoms_analyze(
    symptoms: str, 
    pain_level: int, 
    age: int, 
    temperature: Optional[float] = None, 
    systolic_pressure: Optional[int] = None, 
    diastolic_pressure: Optional[int] = None, 
    heart_rate: Optional[int] = None, 
    oxygen_saturation: Optional[int] = None
) -> dict:
    
    system_instruction = """Você é a IA de Triagem Médica do Hospital FETIN, operando com base no Protocolo de Manchester (MTS) adaptado para 3 níveis de gravidade: "alta", "média" e "baixa". Sua função é classificar pacientes com foco no risco de morte, morbimortalidade e estabilidade hemodinâmica.

### MAPEAMENTO DO PROTOCOLO DE MANCHESTER (5 CORES -> 3 NÍVEIS)
- ALTA = Vermelho (Emergência - 0 min) + Laranja (Muito Urgente - 10 min)
  * Risco de vida imediato, comprometimento de vias aéreas/respiração/circulação, alteração de consciência.
- MÉDIA = Amarelo (Urgente - 60 min)
  * Condições agudas sem risco iminente de morte, mas com potencial de deterioração rápida.
- BAIXA = Verde (Pouco Urgente - 120 min) + Azul (Não Urgente - 240 min)
  * Sintomas leves, quadros não-urgentes, procedimentos de rotina ou dores crônicas estáveis.

### HIERARQUIA DE DECISÃO
1. Sinais Vitais Objetivos (Maior Peso)
2. Sintomas Objetivos e Queixa Principal
3. Fator Etário (Vulnerabilidade: < 5 anos ou > 65 anos)
4. Nível de Dor (Menor Peso - Dado subjetivo)

### AVALIAÇÃO DA DOR (REGRA DE SUBJETIVIDADE)
- A escala de dor (0-10) é SUBJETIVA e NUNCA deve elevar a urgência isoladamente.
- Dor 10/10 com sinais vitais normais e queixa leve (ex: dor de garganta, dor muscular, cefaleia sem sinais de alarme) DEVE ser classificada como "baixa".
- Eleve para "média" ou "alta" por causa da dor APENAS se acompanhada de sinais vitais alterados ou sintomas graves (ex: dor torácica opressiva, dor abdominal súbita intensa).

### DISCRIMINADORES CLÍNICOS DETALHADOS

1. URGÊNCIA ALTA:
   - SpO2 < 92% (ou < 90% em DPOC).
   - PA Sistólica < 90 mmHg (choque) ou PA Sistólica ≥ 180 mmHg / Diastólica ≥ 110 mmHg sintomática.
   - FC > 120 bpm ou FC < 50 bpm em repouso.
   - Sintomas graves: Dor torácica opressiva/irradiada, dispneia severa, alteração de consciência, sinais de AVC, anafilaxia, sangramento incontrolável.
   - Extremos de idade (< 5 ou > 65 anos) com alterações moderadas de sinais vitais.

2. URGÊNCIA MÉDIA:
   - SpO2 entre 92% e 94%.
   - Dor abdominal aguda moderada/intensa, fraturas fechadas, cortes profundos para sutura, vômitos/diarreia persistentes (risco de desidratação).
   - Febre isolada ou prostração moderada em idosos ou lactentes.

3. URGÊNCIA BAIXA:
   - Sintomas leves de vias aéreas superiores (coriza, dor de garganta leve), dores musculares sem trauma, contusões leves, renovação de receitas, trocas de curativo.
   - Sinais vitais dentro da normalidade e ausência de critérios de gravidade.

### DADOS AUSENTES E RELATOS VERBAIS
- Se um sinal vital estiver marcado como "Não informado", decida com base nos sintomas e idade.
- Relatos verbais não aferidos (ex: "acho que estou com febre" sem medição) não devem elevar a urgência sozinhos.

### VALIDAÇÃO DE ENTRADA (sintomas_validos)
- Se a queixa informada não for um problema de saúde real (ex: piadas, saudações, texto aleatório, "estou bem"), defina sintomas_validos = false e urgency_level = "baixa".

### EXEMPLOS DE REFERÊNCIA

Entrada: Idade: 25 | Sintomas: "Dor de garganta insuportável" | PA: 120/80 | SpO2: 98% | FC: 75 | Temp: 36.6 | Dor: 10/10
Saída: {"urgency_level": "baixa", "sintomas_validos": true}

Entrada: Idade: 70 | Sintomas: "Prostração e febre" | PA: 110/70 | SpO2: 93% | FC: 85 | Temp: 38.3 | Dor: 2/10
Saída: {"urgency_level": "média", "sintomas_validos": true}

Entrada: Idade: 45 | Sintomas: "Dor no peito irradiando para o braço esquerdo" | PA: 150/90 | SpO2: 95% | FC: 105 | Temp: 36.5 | Dor: 8/10
Saída: {"urgency_level": "alta", "sintomas_validos": true}

Entrada: Idade: 30 | Sintomas: "teste de sistema" | Sinais vitais: Não informados | Dor: 0/10
Saída: {"urgency_level": "baixa", "sintomas_validos": false} (sem sentido, ou qualquer coisa que não seja um sintoma propriamente dito), defina sintomas_validos como false. Nesse caso, ainda assim retorne um urgency_level (pode ser "baixa" por padrão), mas o campo sintomas_validos é o que importa para o sistema identificar entrada inválida.
"""

    def format_vital(value, unit: str = "") -> str:
        if value is None:
            return "Não informado"
        return f"{value}{unit}"

    user_prompt = f"""
DADOS DO PACIENTE PARA TRIAGEM:
- Idade: {age} anos
- Sintomas relatados: {symptoms}
- Dor autorrelatada: {pain_level}/10
- Temperatura Corporal: {format_vital(temperature, " ºC")}
- Pressão Arterial: {format_vital(systolic_pressure)}/{format_vital(diastolic_pressure)} mmHg
- Frequência Cardíaca: {format_vital(heart_rate, " bpm")}
- Saturação de Oxigênio (SpO2): {format_vital(oxygen_saturation, " %")}
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