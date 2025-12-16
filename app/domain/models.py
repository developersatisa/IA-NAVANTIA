from dataclasses import dataclass
from datetime import date
from typing import Optional
from app.domain.enums import RetirementModality

@dataclass
class RetirementSummary:
    modalidad: RetirementModality
    # Campos comunes o específicos que pueden ser nulos según la modalidad
    f_jubilacion_anticipada_voluntaria: Optional[date] = None
    meses_anticipacion: Optional[int] = None
    coeficiente_reductor_porcentaje: Optional[float] = None
    importe_pension_14_pagas: Optional[float] = None
    
    f_jubilacion_parcial: Optional[date] = None
    porcentaje_reduccion_jornada: Optional[float] = None
