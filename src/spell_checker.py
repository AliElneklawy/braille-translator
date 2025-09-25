from __future__ import annotations

import os
from typing import Optional

try:
    from transformers import AutoTokenizer, T5ForConditionalGeneration
except Exception:  # noqa: BLE001
    AutoTokenizer = None
    T5ForConditionalGeneration = None


class TextCorrection:
    def __init__(self) -> None:
        self.path_to_model = "ai-forever/T5-large-spell"
        self.prefix = "spelling correction: "
        self._enabled_by_env = os.getenv("BRAILLE_ENABLE_SPELL_MODEL", "0").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

        self.model: Optional[T5ForConditionalGeneration] = None
        self.tokenizer: Optional[AutoTokenizer] = None

        if self._enabled_by_env and AutoTokenizer and T5ForConditionalGeneration:
            self.model = T5ForConditionalGeneration.from_pretrained(self.path_to_model)
            self.tokenizer = AutoTokenizer.from_pretrained(self.path_to_model)
        else:
            self._enabled_by_env = False

    def correction(self, uncorrected_text: str) -> str:
        if not uncorrected_text:
            return uncorrected_text

        if not self._enabled_by_env or not self.model or not self.tokenizer:
            return uncorrected_text

        sentence = self.prefix + uncorrected_text
        input_ids = self.tokenizer.encode(sentence, return_tensors="pt")
        output_ids = self.model.generate(input_ids, max_length=512)
        corrected_text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)

        return corrected_text
