from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.application.use_cases import AnalyzeAnticipatedRetirementUseCase, AnalyzePartialRetirementUseCase
from app.infrastructure.openai_client import OpenAIJubilacionAnalyzer
from app.application.dto import AnticipatedRetirementDTO, PartialRetirementDTO

router = APIRouter()

# Dependency Injection (Manual for simplicity, could use FastAPI Depends)
def get_analyzer():
    return OpenAIJubilacionAnalyzer()

@router.post("/jubilacion/anticipada", response_model=AnticipatedRetirementDTO)
async def analyze_anticipada(file: UploadFile = File(...)):
    """
    Analiza un PDF de jubilación anticipada voluntaria y devuelve:
    - modalidad
    - f_jubilacion_anticipada_voluntaria
    - meses_anticipacion
    - coeficiente_reductor_porcentaje
    - importe_pension_14_pagas
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        analyzer = get_analyzer()
        use_case = AnalyzeAnticipatedRetirementUseCase(analyzer)
        
        await file.seek(0)
        file_tuple = (file.filename, file.file)

        result = await use_case.execute(file_tuple)
        
        # Convertir a DTO específico solo con los campos de anticipada
        return AnticipatedRetirementDTO(
            modalidad=result.modalidad,
            f_jubilacion_anticipada_voluntaria=result.f_jubilacion_anticipada_voluntaria,
            meses_anticipacion=result.meses_anticipacion,
            coeficiente_reductor_porcentaje=result.coeficiente_reductor_porcentaje,
            importe_pension_14_pagas=result.importe_pension_14_pagas
        )
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jubilacion/parcial", response_model=PartialRetirementDTO)
async def analyze_parcial(file: UploadFile = File(...)):
    """
    Analiza un PDF de jubilación parcial y devuelve:
    - modalidad
    - importe_pension_14_pagas
    - f_jubilacion_parcial
    - porcentaje_reduccion_jornada
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        analyzer = get_analyzer()
        use_case = AnalyzePartialRetirementUseCase(analyzer)
        
        await file.seek(0)
        file_tuple = (file.filename, file.file)

        result = await use_case.execute(file_tuple)
        
        # Convertir a DTO específico solo con los campos de parcial
        return PartialRetirementDTO(
            modalidad=result.modalidad,
            importe_pension_14_pagas=result.importe_pension_14_pagas,
            f_jubilacion_parcial=result.f_jubilacion_parcial,
            porcentaje_reduccion_jornada=result.porcentaje_reduccion_jornada
        )
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
