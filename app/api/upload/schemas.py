from pydantic import BaseModel
from typing import Optional
from uuid import UUID

# ---

class UploadSuccessData(BaseModel):
    session_id: UUID
    document_type: str
    filename: str
    size: int


class UploadSuccessResponse(BaseModel):
    success: bool
    message: str
    data: UploadSuccessData

# ---

class UploadErrorData(BaseModel):
    error: Optional[str] = None
    filename: Optional[str] = None
    size: Optional[int] = None
    document_type: Optional[str] = None


class UploadErrorResponse(BaseModel):
    success: bool
    message: str
    data: UploadErrorData
