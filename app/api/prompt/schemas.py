from typing import Any
from pydantic import BaseModel, Field


# --- Request

class PromptRequest(BaseModel):
    session_id: str = Field(
        ...,
        description="Existing session identifier",
        example="session_123"
    )
    prompt: str = Field(
        ...,
        description="User prompt to be processed",
        example="Summarize this document"
    )


# --- Response base

class BaseResponse(BaseModel):
    success: bool
    message: str


# --- Success response

class PromptResponseData(BaseModel):
    session_id: str
    response: Any  # LLM output (dict / list / string)


class PromptSuccessResponse(BaseResponse):
    data: PromptResponseData


# --- Error response

class PromptErrorData(BaseModel):
    session_id: str


class PromptErrorResponse(BaseResponse):
    data: PromptErrorData
