from pydantic import BaseModel
from datetime import date
from app.domain.enums import RetirementModality

class AnticipatedRetirementDTO(BaseModel):
    """DTO específico para jubilación anticipada voluntaria"""
    modalidad: RetirementModality
    f_jubilacion_anticipada_voluntaria: date
    meses_anticipacion: int
    coeficiente_reductor_porcentaje: float
    importe_pension_14_pagas: float

class PartialRetirementDTO(BaseModel):
    """DTO específico para jubilación parcial"""
    modalidad: RetirementModality
    importe_pension_14_pagas: float
    f_jubilacion_parcial: date
    porcentaje_reduccion_jornada: float
