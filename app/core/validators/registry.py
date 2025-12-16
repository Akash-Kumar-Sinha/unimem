import magic
from app.core.validators.pdf import PDFValidator
from app.core.validators.image import ImageValidator
from app.core.document_types import DocumentType

_VALIDATORS = {
    "application/pdf": PDFValidator(),
    "image/png": ImageValidator(),
    "image/jpeg": ImageValidator(),
    "image/webp": ImageValidator(),
}

def validate_document(content: bytes) -> DocumentType:
    mime = magic.from_buffer(content, mime=True)

    validator = _VALIDATORS.get(mime)
    if not validator:
        raise ValueError(f"Unsupported file type: {mime}")

    validator.validate(content) # Calling validate funtion, to actually validate the provided document.
    return validator.document_type
