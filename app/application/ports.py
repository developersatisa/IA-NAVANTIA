from abc import ABC, abstractmethod
from typing import BinaryIO
from app.domain.models import RetirementSummary

class DocumentAnalyzerPort(ABC):
    @abstractmethod
    def analyze_anticipada(self, pdf_file: BinaryIO) -> RetirementSummary:
        pass

    @abstractmethod
    def analyze_parcial(self, pdf_file: BinaryIO) -> RetirementSummary:
        pass
