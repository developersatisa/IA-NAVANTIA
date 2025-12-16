import json
import asyncio
from typing import BinaryIO
from openai import OpenAI
from app.application.ports import DocumentAnalyzerPort
from app.domain.models import RetirementSummary
from app.domain.enums import RetirementModality
from app.infrastructure.config import config

PROMPT_JUBILACION_ANTICIPADA = """
Eres una IA especializada en extraer información de documentos de cálculo de pensión de la Seguridad Social española, concretamente de JUBILACIÓN ANTICIPADA VOLUNTARIA.

Recibirás un único PDF como entrada. Lee TODO el documento (encabezados, tablas y notas) y devuelve EXCLUSIVAMENTE un JSON válido con esta estructura:

{
  "modalidad": "jubilacion_anticipada_voluntaria",
  "f_jubilacion_anticipada_voluntaria": "YYYY-MM-DD",
  "meses_anticipacion": <numero entero>,
  "coeficiente_reductor_porcentaje": <numero>,
  "importe_pension_14_pagas": <numero>
}

REGLAS GENERALES
- No añadas ningún texto fuera del JSON.
- Usa exactamente esos nombres de campos.
- Los valores numéricos deben ir SIN símbolo de euro y SIN símbolo de porcentaje, con punto decimal si hace falta (ejemplo: 3048.02, 17.6).
- Convierte todas las fechas del tipo DD/MM/AAAA a formato ISO "YYYY-MM-DD".
- Si necesitas hacer alguna operación sencilla (por ejemplo 100 - 82.4), hazla tú y devuelve el resultado numérico.

CÓMO LOCALIZAR CADA CAMPO EN DOCUMENTOS TIPO "CÁLCULO DE BASE REGULADORA A 300 MESES":

- "f_jubilacion_anticipada_voluntaria":
  - Usa la fecha que aparece como "Fecha jubilación" en el encabezado del documento.

- "meses_anticipacion":
  - Usa el valor que aparece junto a "Meses de anticipación" o similar, en el bloque donde se indica el cálculo por anticipación.

- "coeficiente_reductor_porcentaje":
  - IMPORTANTE: Primero verifica si el documento contiene alguna de estas frases indicando aplicación del límite máximo:
    * "Dado que la base reguladora de la pensión es superior al límite máximo de las pensiones públicas"
    * "segundo párrafo del artículo 210.3 LGSS"
    * "Al ser la base reguladora de la pensión calculada superior al límite máximo"

  - SI ENCUENTRA ALGUNA DE ESAS FRASES:
    * Busca el coeficiente reductor que se menciona en relación al límite máximo de pensiones públicas.
    * Normalmente aparecerá en un texto como: "el coeficiente reductor de [X] %, se aplica sobre el límite máximo de las pensiones públicas"
    * Usa ese valor X como coeficiente_reductor_porcentaje.
    * Ejemplo: si dice "coeficiente reductor de una tabla específica 6.72 %, se aplica sobre el límite máximo" → usa 6.72

  - SI NO ENCUENTRA ESAS FRASES (caso normal):
    * Si ves un texto de "porcentaje de descuento" por anticipar la jubilación (por ejemplo, "descuento del 17,6 %"), usa ese número.
    * Si NO aparece explícitamente, pero ves un "Porcentaje anticipada" o "Porcentaje reductor por anticipación" con un valor X (por ejemplo, 82,40 %),
      interpreta que el coeficiente reductor es la parte que se pierde:
        coeficiente_reductor_porcentaje = 100 - X

- "importe_pension_14_pagas":
  - Utiliza el importe FINAL de la pensión anticipada mensual en 14 pagas.
  - Si el documento muestra primero una "pensión ordinaria" (por ejemplo, 3.009,81 €) y luego indica que se limita por el máximo de pensiones públicas a otra cantidad (por ejemplo, 3.048,02 €), usa ese último importe como "importe_pension_14_pagas".
  - Si no se menciona límite máximo, usa la pensión resultante definitiva de jubilación anticipada.

Devuelve SOLO el JSON con estos 5 campos, sin explicaciones adicionales.
"""

PROMPT_JUBILACION_PARCIAL = """
Eres una IA especializada en extraer información de documentos de cálculo de pensión de la Seguridad Social española, concretamente de JUBILACIÓN PARCIAL.

Recibirás un único PDF como entrada. Lee TODO el documento y devuelve EXCLUSIVAMENTE un JSON válido con esta estructura:

{
  "modalidad": "jubilacion_parcial",
  "importe_pension_14_pagas": <numero>,
  "f_jubilacion_parcial": "YYYY-MM-DD",
  "porcentaje_reduccion_jornada": <numero>
}

REGLAS GENERALES
- No añadas ningún texto fuera del JSON.
- Usa exactamente esos nombres de campos.
- Los valores numéricos deben ir SIN símbolo de euro y SIN símbolo de porcentaje, con punto decimal si hace falta (ejemplo: 2748.26, 75.0).
- Convierte todas las fechas del tipo DD/MM/AAAA a formato ISO "YYYY-MM-DD".

CÓMO LOCALIZAR CADA CAMPO:

- "f_jubilacion_parcial":
  - Usa la fecha que figura como "Fecha hecho causante" en el encabezado del documento (es la referencia típica para jubilación parcial).

- "porcentaje_reduccion_jornada":
  - Si aparece un campo "% reducción de jornada", utiliza ese valor.
  - Si no aparece, pero ves un "Porcentaje jubilación parcial: 75,00 %", utiliza ese valor como porcentaje de reducción de jornada.

- "importe_pension_14_pagas":
  - Usa el importe que aparezca como "Importe jubilación parcial" o campo equivalente que indique la pensión mensual en 14 pagas (por ejemplo, "Importe jubilación parcial: 2.748,26 €" → 2748.26).

Devuelve SOLO el JSON con estos 4 campos, sin explicaciones adicionales.
"""

class OpenAIJubilacionAnalyzer(DocumentAnalyzerPort):
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL

    async def analyze_anticipada(self, pdf_file: BinaryIO) -> RetirementSummary:
        return await self._run_analysis(pdf_file, PROMPT_JUBILACION_ANTICIPADA, RetirementModality.JUBILACION_ANTICIPADA_VOLUNTARIA)

    async def analyze_parcial(self, pdf_file: BinaryIO) -> RetirementSummary:
        return await self._run_analysis(pdf_file, PROMPT_JUBILACION_PARCIAL, RetirementModality.JUBILACION_PARCIAL)

    async def _run_analysis(self, pdf_file: BinaryIO, prompt: str, expected_modality: RetirementModality) -> RetirementSummary:
        uploaded_file = None
        try:
            # 1. Upload File (run in thread pool to avoid blocking)
            uploaded_file = await asyncio.to_thread(
                self.client.files.create,
                file=pdf_file,
                purpose="user_data"
            )

            # 2. Call Model (run in thread pool to avoid blocking)
            response = await asyncio.to_thread(
                self.client.responses.create,
                model=self.model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_file", "file_id": uploaded_file.id},
                            {"type": "input_text", "text": prompt}
                        ]
                    }
                ]
            )

            # 3. Get Output
            raw_json = response.output_text

            # 4. Parse JSON
            data = json.loads(raw_json)

            # 5. Convert to Domain Model según modalidad
            if expected_modality == RetirementModality.JUBILACION_ANTICIPADA_VOLUNTARIA:
                return RetirementSummary(
                    modalidad=RetirementModality.JUBILACION_ANTICIPADA_VOLUNTARIA,
                    f_jubilacion_anticipada_voluntaria=self._parse_date(data.get("f_jubilacion_anticipada_voluntaria")),
                    meses_anticipacion=data.get("meses_anticipacion"),
                    coeficiente_reductor_porcentaje=data.get("coeficiente_reductor_porcentaje"),
                    importe_pension_14_pagas=data.get("importe_pension_14_pagas")
                )
            else:  # JUBILACION_PARCIAL
                return RetirementSummary(
                    modalidad=RetirementModality.JUBILACION_PARCIAL,
                    importe_pension_14_pagas=data.get("importe_pension_14_pagas"),
                    f_jubilacion_parcial=self._parse_date(data.get("f_jubilacion_parcial")),
                    porcentaje_reduccion_jornada=data.get("porcentaje_reduccion_jornada")
                )

        except Exception as e:
            print(f"Error analyzing document: {e}")
            raise e
        finally:
            # 6. Delete File (run in thread pool to avoid blocking)
            if uploaded_file:
                try:
                    await asyncio.to_thread(self.client.files.delete, uploaded_file.id)
                except Exception as cleanup_error:
                    print(f"Error deleting file: {cleanup_error}")

    def _parse_date(self, date_str: str):
        if not date_str:
            return None
        from datetime import datetime
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
