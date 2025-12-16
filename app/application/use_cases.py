from typing import BinaryIO
from app.application.ports import DocumentAnalyzerPort
from app.domain.models import RetirementSummary

class AnalyzeAnticipatedRetirementUseCase:
    def __init__(self, analyzer: DocumentAnalyzerPort):
        self.analyzer = analyzer

    async def execute(self, pdf_file: BinaryIO) -> RetirementSummary:
        return await self.analyzer.analyze_anticipada(pdf_file)

class AnalyzePartialRetirementUseCase:
    def __init__(self, analyzer: DocumentAnalyzerPort):
        self.analyzer = analyzer

    async def execute(self, pdf_file: BinaryIO) -> RetirementSummary:
        return await self.analyzer.analyze_parcial(pdf_file)
