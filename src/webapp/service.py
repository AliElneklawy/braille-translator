from __future__ import annotations

import shutil
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Union
from uuid import uuid4

from fastapi import HTTPException

from ..inference import Inference
from ..process_images import ProcessImage
from ..spell_checker import TextCorrection
from ..TTS import TTS


ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


@dataclass
class TranslationResult:
    raw_text: str
    corrected_text: str
    audio_path: Optional[Path]
    audio_url: Optional[str]
    correction_applied: bool


class BrailleTranslatorService:
    def __init__(
        self,
        model_path: Path,
        media_root: Path,
        temp_root: Optional[Path] = None,
        enable_correction: bool = False,
        enable_tts: bool = True,
        max_audio_age_hours: int = 24,
        cleanup_interval_hours: int = 1,
    ) -> None:
        if not model_path.exists():
            raise FileNotFoundError(
                f"Braille translation model was not found at {model_path!s}"
            )

        self.model_path = model_path
        self.media_root = media_root
        self.media_root.mkdir(parents=True, exist_ok=True)
        self.audio_dir = self.media_root / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        self.temp_root = temp_root or Path(tempfile.gettempdir()) / "braille_webapp"
        self.temp_root.mkdir(parents=True, exist_ok=True)
        
        self.max_audio_age = timedelta(hours=max_audio_age_hours)
        self.cleanup_interval = timedelta(hours=cleanup_interval_hours)
        self._last_cleanup = datetime.min

        self._inference = Inference(str(self.model_path))
        self._enable_correction = enable_correction
        self._correction_model: Optional[TextCorrection] = None
        self._enable_tts = enable_tts
        self._tts_engine: Optional[TTS] = None

    def _ensure_correction_model(self) -> TextCorrection:
        if not self._enable_correction:
            raise RuntimeError("Spell correction is disabled")
        if self._correction_model is None:
            self._correction_model = TextCorrection()
        return self._correction_model

    def _ensure_tts_engine(self) -> TTS:
        if not self._enable_tts:
            raise RuntimeError("Text-to-speech is disabled")
        if self._tts_engine is None:
            self._tts_engine = TTS()
        return self._tts_engine

    def save_upload(self, filename: str, data: bytes) -> Path:
        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail="Unsupported file type. Please upload a valid image file.",
            )
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix or ".png",
            dir=self.temp_root,
        )
        temp_file.write(data)
        temp_file.flush()
        temp_file.close()
        return Path(temp_file.name)

    def translate_image(
        self,
        image_path: Path,
        generate_audio: bool = True,
        apply_correction: Optional[bool] = None,
    ) -> TranslationResult:
        processing_dir = Path(
            tempfile.mkdtemp(prefix="braille_proc_", dir=self.temp_root)
        )
        try:
            processor = ProcessImage(str(image_path), temp_dir=str(processing_dir))
            symbols = processor.divide_the_image_return_array_of_images()
            if not symbols:
                raise HTTPException(
                    status_code=422,
                    detail="Unable to detect Braille symbols in the provided image.",
                )

            preprocessed = self._inference.preprocess(symbols)
            encoded = [self._inference.predict(img) for img in preprocessed]
            raw_text = self._inference.decode(encoded).strip()

            corrected_text = raw_text
            correction_applied = False
            effective_correction = (
                self._enable_correction
                if apply_correction is None
                else self._enable_correction and apply_correction
            )
            if effective_correction and raw_text:
                try:
                    corrected_text = self._ensure_correction_model().correction(raw_text)
                    correction_applied = True
                except Exception as exc:  # noqa: BLE001
                    raise HTTPException(
                        status_code=500,
                        detail="Spell correction failed. Please try again later.",
                    ) from exc

            audio_path: Optional[Path] = None
            audio_url: Optional[str] = None

            if generate_audio and corrected_text:
                try:
                    audio_filename = f"tts_{uuid4().hex}.wav"
                    audio_engine = self._ensure_tts_engine()
                    audio_path = audio_engine.save_file(
                        corrected_text,
                        output_dir=self.audio_dir,
                        filename=audio_filename,
                    )
                    audio_url = f"/media/audio/{audio_path.name}"
                except Exception as exc:  # noqa: BLE001
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to generate audio. Please try again later.",
                    ) from exc

            return TranslationResult(
                raw_text=raw_text,
                corrected_text=corrected_text,
                audio_path=audio_path,
                audio_url=audio_url,
                correction_applied=correction_applied,
            )
        finally:
            try:
                image_path.unlink(missing_ok=True)
            except Exception:  # noqa: BLE001
                pass
            shutil.rmtree(processing_dir, ignore_errors=True)

    def cleanup_old_files(self, force: bool = False) -> None:
        """Clean up old audio and temporary files.
        
        Args:
            force: If True, perform cleanup regardless of the cleanup interval.
        """
        now = datetime.now()
        if not force and (now - self._last_cleanup) < self.cleanup_interval:
            return
            
        self._last_cleanup = now
        
        # Clean up old audio files
        if self.audio_dir.exists():
            for audio_file in self.audio_dir.glob('*'):
                try:
                    file_age = datetime.fromtimestamp(audio_file.stat().st_mtime)
                    if now - file_age > self.max_audio_age:
                        audio_file.unlink(missing_ok=True)
                except (OSError, AttributeError):
                    continue
        
        # Clean up old temporary directories
        if self.temp_root.exists():
            max_temp_age = timedelta(hours=1)  # Shorter TTL for temp files
            for temp_dir in self.temp_root.glob('braille_proc_*'):
                try:
                    if temp_dir.is_dir():
                        dir_age = datetime.fromtimestamp(temp_dir.stat().st_mtime)
                        if now - dir_age > max_temp_age:
                            shutil.rmtree(temp_dir, ignore_errors=True)
                except (OSError, AttributeError):
                    continue

    def translate_bytes(
        self,
        filename: str,
        data: bytes,
        generate_audio: bool = True,
        apply_correction: Optional[bool] = None,
    ) -> TranslationResult:
        # Clean up old files before processing new request
        self.cleanup_old_files()
        
        image_path = self.save_upload(filename, data)
        return self.translate_image(
            image_path,
            generate_audio=generate_audio,
            apply_correction=apply_correction,
        )
