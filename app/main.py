from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import Settings, get_settings
from app.schemas import ChatRequest, ChatResponse
from app.services.assistant_service import AssistantService


app = FastAPI(
    title="Jarvis Local Assistant",
    version="1.0.0",
    description="Kompyuterni boshqarish va kod bilan ishlash uchun lokal AI yordamchi.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_assistant_service(
    settings: Settings = Depends(get_settings),
) -> AssistantService:
    return AssistantService(settings=settings)


@app.get("/")
def index(settings: Settings = Depends(get_settings)) -> FileResponse:
    index_file = settings.static_dir / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend topilmadi.")
    return FileResponse(index_file)


@app.get("/api/health")
def health(settings: Settings = Depends(get_settings)) -> dict[str, str | bool]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "workspace": str(settings.workspace_dir),
        "llm_enabled": bool(settings.openai_api_key),
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    assistant: AssistantService = Depends(get_assistant_service),
) -> ChatResponse:
    return assistant.handle_message(payload.message)


app.mount("/static", StaticFiles(directory=get_settings().static_dir), name="static")
