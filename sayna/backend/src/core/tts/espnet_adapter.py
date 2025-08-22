"""
Coqui TTS Adapter for SAYNA.
Provides multilingual text-to-speech with a focus on African languages.
"""

import asyncio
import logging
from typing import Optional, Dict, List, Tuple, Any

import numpy as np
import torch
from typeguard import typechecked
from TTS.api import TTS  # why isnt this working??

from sayna.backend.src.core.utils.audio import save_audio_to_bytes

logger = logging.getLogger(__name__)


class CoquiTTSAdapter:
    """Coqui-based Text-to-Speech adapter for African languages."""

    _instance: Optional["CoquiTTSAdapter"] = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.models: Dict[str, TTS] = {}
        self.supported_languages = {
            "en": "English",
            "yo": "Yoruba",
            "ha": "Hausa",
            "ig": "Igbo",
            "sw": "Swahili"
        }
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sample_rate = 22050  # Coqui defaults, can be model-specific

    @classmethod
    async def get_instance(cls) -> "CoquiTTSAdapter":
        """Get singleton instance of CoquiTTSAdapter."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._initialize()
        return cls._instance

    async def _initialize(self) -> None:
        """Initialize the TTS models."""
        try:
            logger.info("Initializing Coqui TTS models...")

            # Load models for each supported language
            for lang_code in self.supported_languages:
                try:
                    await self._load_model(lang_code)
                except Exception as e:
                    logger.warning(f"Could not load TTS model for {lang_code}: {e}")

            logger.info(f"TTS initialized with {len(self.models)} language models")

        except Exception as e:
            logger.error(f"Failed to initialize CoquiTTSAdapter: {e}")
            raise

    async def _load_model(self, lang_code: str) -> None:
        """Load a specific language model."""

        logger.info(f"Loading Coqui TTS model for {lang_code}...")

        # Choose model — fallback multilingual model for unsupported languages
        # You can swap this out for fine-tuned African language models later
        if lang_code == "en":
            model_name = "tts_models/en/ljspeech/tacotron2-DDC"
        else:
            # Multilingual model that supports many languages (including African ones with some accents)
            model_name = "tts_models/multilingual/multi-dataset/your_tts"

        loop = asyncio.get_event_loop()
        model = await loop.run_in_executor(
            None,
            lambda: TTS(model_name).to(self.device)
        )

        self.models[lang_code] = model
        logger.info(f"TTS model for {lang_code} loaded successfully")

    @typechecked
    async def synthesize(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None,
        speed: float = 1.0,
        output_format: str = "wav",
    ) -> bytes:
        """
        Synthesize speech from text.

        Args:
            text: Input text to synthesize
            language: Language code (e.g., 'en', 'yo')
            voice: Voice ID (optional)
            speed: Speech rate (0.5-2.0)
            output_format: Audio format ('wav', 'mp3', etc.)

        Returns:
            Audio data in bytes
        """
        try:
            if language not in self.supported_languages:
                raise ValueError(f"Language {language} not supported")

            if language not in self.models:
                raise ValueError(f"No TTS model loaded for {language}")

            # Validate speed
            speed = max(0.5, min(2.0, speed))

            logger.info(f"Synthesizing {len(text)} chars in {language}...")

            loop = asyncio.get_event_loop()
            audio, params = await loop.run_in_executor(
                None,
                self._synthesize_sync,
                text,
                language,
                speed,
                voice,
            )

            # Convert to requested format
            audio_bytes = save_audio_to_bytes(
                audio,
                sample_rate=params["sr"],
                format=output_format,
            )

            logger.info(f"TTS synthesis completed ({len(audio_bytes)} bytes)")
            return audio_bytes

        except Exception as e:
            logger.error(f"Error in TTS synthesis: {e}")
            raise

    def _synthesize_sync(
        self, text: str, language: str, speed: float, voice: Optional[str]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Synchronous synthesis method for thread execution."""
        model = self.models[language]

        # Preprocess text
        text = self._preprocess_text(text, language)

        # Run synthesis (Coqui API)
        wav = model.tts(text)

        # Adjust speed by resampling if needed
        if speed != 1.0:
            wav = np.interp(
                np.arange(0, len(wav), speed),
                np.arange(0, len(wav)),
                wav,
            )

        return wav.astype(np.float32), {"sr": self.sample_rate}

    def _preprocess_text(self, text: str, language: str) -> str:
        """Preprocess text for TTS input."""
        text = text.strip()

        if language == "yo":
            text = self._preprocess_yoruba(text)
        elif language == "ha":
            text = self._preprocess_hausa(text)
        elif language == "ig":
            text = self._preprocess_igbo(text)
        elif language == "sw":
            text = self._preprocess_swahili(text)

        return text

    def _preprocess_yoruba(self, text: str) -> str:
        return text

    def _preprocess_hausa(self, text: str) -> str:
        return text

    def _preprocess_igbo(self, text: str) -> str:
        return text

    def _preprocess_swahili(self, text: str) -> str:
        return text

    async def get_available_voices(self, language: str) -> List[Dict[str, str]]:
        """Get available voices for a language."""
        if language not in self.supported_languages:
            return []

        # Placeholder voices (Coqui supports cloning / multiple voices per model)
        return [
            {"id": "default", "name": "Default Voice", "gender": "female"},
            {"id": "male", "name": "Male Voice", "gender": "male"},
        ]

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on TTS system."""
        return {
            "healthy": True,
            "loaded_models": list(self.models.keys()),
            "supported_languages": list(self.supported_languages.keys()),
            "device": self.device,
            "sample_rate": self.sample_rate,
        }
