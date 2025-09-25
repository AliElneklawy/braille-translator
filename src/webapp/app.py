from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .service import BrailleTranslatorService, TranslationResult

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
MEDIA_DIR = BASE_DIR / "media"

TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Braille Translator Web App", version="1.0.0")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class Settings(BaseSettings):
    model_path: Path = Field(
        default=BASE_DIR.parent.parent / "models" / "grade_1_model.h5",
        description="Path to the trained Braille translation model.",
    )
    enable_spell_correction: bool = Field(
        default=True,
        description="Flag to enable or disable spell correction stage.",
    )
    enable_tts: bool = Field(
        default=True,
        description="Flag to enable or disable text-to-speech generation.",
    )

    model_config = SettingsConfigDict(
        env_prefix="BRAILLE_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


@lru_cache()
def get_service() -> BrailleTranslatorService:
    settings = get_settings()
    try:
        return BrailleTranslatorService(
            model_path=settings.model_path,
            media_root=MEDIA_DIR,
            enable_correction=settings.enable_spell_correction,
            enable_tts=settings.enable_tts,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Braille translation model not found. Please check BRAILLE_MODEL_PATH."
        ) from exc


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    settings = get_settings()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None,
            "error_message": None,
            "settings": settings,
            "current_year": datetime.now().year,
            "generate_audio": settings.enable_tts,
            "apply_correction": settings.enable_spell_correction,
        },
    )


@app.post("/translate", response_class=HTMLResponse)
async def translate(
    request: Request,
    file: UploadFile = File(...),
    generate_audio: Optional[str] = Form(None),
    apply_correction: Optional[str] = Form(None),
    settings: Settings = Depends(get_settings),
    service: BrailleTranslatorService = Depends(get_service),
) -> HTMLResponse:
    if not file.filename:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": None,
                "error_message": "Please select an image before submitting.",
                "settings": settings,
                "current_year": datetime.now().year,
                "generate_audio": settings.enable_tts,
            },
            status_code=400,
        )

    file_bytes = await file.read()

    generate_audio_flag = False
    if settings.enable_tts:
        if generate_audio is not None:
            generate_audio_flag = str(generate_audio).lower() in {"1", "true", "on", "yes"}
        else:
            generate_audio_flag = False

    apply_correction_flag = False
    if settings.enable_spell_correction:
        if apply_correction is not None:
            apply_correction_flag = str(apply_correction).lower() in {"1", "true", "on", "yes"}
        else:
            apply_correction_flag = False

    try:
        result: TranslationResult = await run_in_threadpool(
            service.translate_bytes,
            file.filename,
            file_bytes,
            generate_audio=generate_audio_flag,
            apply_correction=apply_correction_flag,
        )
    except HTTPException as exc:
        status_code = exc.status_code
        detail = exc.detail
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": None,
                "error_message": detail,
                "settings": settings,
                "current_year": datetime.now().year,
                "generate_audio": generate_audio_flag,
                "apply_correction": apply_correction_flag,
            },
            status_code=status_code,
        )
    except RuntimeError as exc:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": None,
                "error_message": str(exc),
                "settings": settings,
                "current_year": datetime.now().year,
                "generate_audio": generate_audio_flag,
                "apply_correction": apply_correction_flag,
            },
            status_code=500,
        )
    except Exception as exc:  # noqa: BLE001, F841
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": None,
                "error_message": "An unexpected error occurred during translation.",
                "settings": settings,
                "current_year": datetime.now().year,
                "generate_audio": generate_audio_flag,
                "apply_correction": apply_correction_flag,
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "error_message": None,
            "settings": settings,
            "current_year": datetime.now().year,
            "generate_audio": generate_audio_flag,
            "apply_correction": apply_correction_flag,
        },
    )


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
