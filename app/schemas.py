from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    speak_reply: bool = True


class ActionPayload(BaseModel):
    name: str
    status: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    reply: str
    source: str
    action: ActionPayload | None = None
