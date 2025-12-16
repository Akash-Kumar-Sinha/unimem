import pymupdf
from app.core.validators.base import DocumentValidator
from app.core.document_types import DocumentType

class PDFValidator(DocumentValidator):
    document_type = DocumentType.PDF

    def validate(self, content: bytes) -> None:
        try:
            pymupdf.open(stream=content, filetype="pdf")
        except Exception as e:
            raise ValueError("Invalid PDF file") from e
