from abc import ABC, abstractmethod
from app.core.document_types import DocumentType

class DocumentValidator(ABC):
    document_type: DocumentType

    @abstractmethod
    def validate(self, content: bytes) -> None:
        """
        Raise ValueError if invalid
        """
        pass
