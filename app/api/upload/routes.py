# External imports
import os, uuid
from fastapi import APIRouter, UploadFile, BackgroundTasks, HTTPException, status
from pathlib import Path

# Local imports
from app.config.config import UPLOAD_DIR, LOG_LEVEL_DEBUG, APPLICATION_LOG_FILE, MAX_DOCUMENT_SIZE
from app.core.logger import setup_logger
from app.core.process_document import ProcessDocument
from app.core.validators.registry import validate_document
from app.api.upload.schemas import (
    UploadSuccessResponse,
    UploadErrorResponse,
)


# Initialization
router = APIRouter()
pd = ProcessDocument()
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)
UPLOAD_DIR = Path(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_IMAGE_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp"
}

ALLOWED_PDF_MIME_TYPE = "application/pdf"

# ---

@router.put(
    "/upload",
    response_model=UploadSuccessResponse,
    responses={
        400: {"model": UploadErrorResponse},
        413: {"model": UploadErrorResponse},
        500: {"model": UploadErrorResponse},
    },
    summary="Upload and validate a document",
    description="Uploads a PDF or image, validates it, and starts background processing.",
)
async def process_file(
    file: UploadFile,
    background_tasks: BackgroundTasks,
) -> UploadSuccessResponse:
    
    session_id = uuid.uuid4() # To map each document with the ID
    safe_name = f"{session_id}{Path(file.filename).suffix}"
    file_path = UPLOAD_DIR / safe_name
    
    try:
        contents = await file.read()
        size = len(contents)

        if size > MAX_DOCUMENT_SIZE:
            raise HTTPException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail={
            "success": False,
            "message": "Only files with size under 1 MB are supported",
            "data": {
                "filename": file.filename,
                "size": size,
            },
        },
    )

        doc_type = validate_document(contents)
        file_path.write_bytes(contents)
        logger.info(f"Uploaded file saved in {file_path}")

    # Catch validation error thorwn by validator
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "Upload a valid file",
                "data": {
                    "error": str(e),
                    "filename": file.filename,
                },
            },
        )

    # Catch unexpected exceptions/errors
    except Exception as e:
        logger.exception("Unexpected upload error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Unexpected error while processing the file",
                "data": {
                    "error": str(e),
                    "filename": file.filename,
                },
            },
        )


    background_tasks.add_task(
        pd.process,
        str(file_path),
        doc_type.value,
        str(session_id),
    )

    
    return UploadSuccessResponse(
        success=True,
        message="File uploaded successfully",
        data={
            "session_id": session_id,
            "document_type": doc_type.value,
            "filename": file.filename,
            "size": size,
        },
    )
