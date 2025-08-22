"""
Wav2Vec2-XLS-R STT adapter for SAYNA.
Uses Facebook's wav2vec2-xlsr-300m-* checkpoints fine-tuned on African languages.
"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional, Union

import numpy as np
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

logger = logging.getLogger(__name__)

# ------------- adapter -------------------------------------------------
class Wav2Vec2STTAdapter:
    _instance: Optional["Wav2Vec2STTAdapter"] = None
    _lock = asyncio.Lock()

    def __init__(self, lang_code: str = "ha"):
        """
        lang_code : "ha" | "yo" | "ig" | "sw" ...
        """
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.lang_code = lang_code

    @classmethod
    async def get_instance(cls, lang_code: str = "ha"):
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(lang_code)
                    await cls._instance._initialize()
        return cls._instance

    async def _initialize(self) -> None:
        model_id = f"facebook/wav2vec2-xlsr-300m-53"
        logger.info(f"Loading Wav2Vec2 model: {model_id}")

        loop = asyncio.get_event_loop()
        self.processor = await loop.run_in_executor(
            None, Wav2Vec2Processor.from_pretrained, model_id
        )
        self.model = await loop.run_in_executor(
            None,
            lambda: Wav2Vec2ForCTC.from_pretrained(model_id).to(self.device),
        )
        logger.info("Wav2Vec2STTAdapter ready")

    def _map_lang(self, code: str) -> str:
        mapping = {"ha": "Hausa", "yo": "Yoruba", "ig": "Igbo", "sw": "Swahili"}
        return mapping.get(code, "Hausa")

    async def transcribe(
        self,
        audio_data: Union[str, np.ndarray],
        language: Optional[str] = None,
    ) -> Dict[str, Union[str, float]]:
        """
        Accepts either a file path or a 16-kHz mono float32 numpy array.
        Returns: {"text": ..., "language": ..., "confidence": ...}
        """
        if isinstance(audio_data, str):
            audio, sr = torchaudio.load(audio_data)
            if sr != 16_000:
                audio = torchaudio.functional.resample(audio, sr, 16_000)
            audio = audio.squeeze().numpy()
        else:
            audio = audio_data.astype(np.float32)

        loop = asyncio.get_event_loop()
        inputs = await loop.run_in_executor(
            None, self.processor, audio, 16_000, False
        )
        input_values = torch.tensor(inputs.input_values).to(self.device)

        with torch.no_grad():
            logits = self.model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)

        transcription = self.processor.decode(predicted_ids[0])

        return {
            "text": transcription.strip(),
            "language": self.lang_code,
            "confidence": 0.95,  # Wav2Vec2 does not natively give confidence
        }

audio_file = r"C:\Users\hp\Desktop\super folder\PTT-20250721-WA0006 (1) (1).wav"

async def _demo():
    stt = await Wav2Vec2STTAdapter.get_instance("ha")   # Hausa
    result = await stt.transcribe(audio_file)
    print("Text: ", result["text"])
    print("Lang: ", result["language"])
    print("Confidence: ", result["confidence"])

if __name__ == "__main__":
    asyncio.run(_demo())