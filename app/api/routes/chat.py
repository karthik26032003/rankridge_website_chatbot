from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.rate_limit import enforce_rate_limit
from app.services.chat_service import (
    start_chat_message,
    stream_chat_response,
)
from app.services.memory_service import get_chat_messages

router = APIRouter()

MAX_MESSAGE_LENGTH = 2000


class StartChatRequest(BaseModel):
    chat_id: str
    message: str


@router.post("/chat/start", dependencies=[Depends(enforce_rate_limit)])
def start_chat_endpoint(request: StartChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    if len(message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Message is too long (max {MAX_MESSAGE_LENGTH} characters)."
        )

    message_id = start_chat_message(request.chat_id, message)
    return {
        "chat_id": request.chat_id,
        "message_id": message_id
    }


@router.post("/chat/stream", dependencies=[Depends(enforce_rate_limit)])
def stream_chat_endpoint(request: StartChatRequest):
    return StreamingResponse(
        stream_chat_response(request.chat_id),
        media_type="text/plain"
    )


@router.get("/chat/{chat_id}")
def get_chat_session_endpoint(chat_id: str):
    return get_chat_messages(chat_id)
