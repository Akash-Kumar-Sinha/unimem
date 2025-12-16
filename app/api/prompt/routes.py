# External imports
import os, json
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pathlib import Path

# Local imports
from app.config.config import UPLOAD_DIR, LOG_LEVEL_DEBUG, APPLICATION_LOG_FILE
from app.core.process_prompt import ProcessPrompt
from app.core.logger import setup_logger
from app.db.manager import session_exists
from app.api.prompt.schemas import (
    PromptRequest,
    PromptSuccessResponse,
    PromptErrorResponse,
    PromptResponseData,
)

# Initialization
router = APIRouter()
pp = ProcessPrompt()
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)
UPLOAD_DIR = Path(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Logic
@router.post(
    "/prompt",
    response_model=PromptSuccessResponse,
    responses={404: {"model": PromptErrorResponse}},
)
async def process_prompt(
    data: PromptRequest,
    background_tasks: BackgroundTasks,
):
    if session_exists(session_id=data.session_id):
        answer = pp.process(data.session_id, data.prompt)
        answer = json.loads(answer)

        return PromptSuccessResponse(
            success=True,
            message="Prompt processed successfully",
            data=PromptResponseData(
                session_id=data.session_id,
                response=answer,
            ),
        )

    raise HTTPException(
        status_code=404,
        detail={
            "success": False,
            "message": "Provided session_id does not exist in database",
            "data": {"session_id": data.session_id},
        },
    )
