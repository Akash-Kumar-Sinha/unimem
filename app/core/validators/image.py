import io
from PIL import Image
from app.core.validators.base import DocumentValidator
from app.core.document_types import DocumentType
from app.config.config import MAX_IMAGE_DIMENSION

class ImageValidator(DocumentValidator):
    document_type = DocumentType.IMAGE

    def validate(self, content: bytes) -> None:
        try:
            img = Image.open(io.BytesIO(content))
            img.verify()

            if img.width > MAX_IMAGE_DIMENSION or img.height > MAX_IMAGE_DIMENSION:
                raise ValueError("Image dimensions too large")

        except Exception as e:
            raise ValueError("Invalid image file") from e
