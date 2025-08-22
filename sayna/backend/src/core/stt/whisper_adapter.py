"""
Enhanced Whisper STT (Speech-to-Text) adapter using Faster-Whisper.
Provides high-performance multilingual speech recognition for African languages.
"""

import asyncio
import logging
from typing import Dict, Optional, Union
from pathlib import Path

import numpy as np
import torch
from faster_whisper import WhisperModel

from sayna.backend.src.core.stt.language_detector import LanguageDetector
from sayna.backend.src.core.utils.audio import preprocess_audio

logger = logging.getLogger(__name__)


class FastWhisperSTTAdapter:
    """High-performance Whisper STT adapter using Faster-Whisper for African languages."""

    _instance: Optional['FastWhisperSTTAdapter'] = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.model = None
        self.language_detector = None

        # Use small model for optimal speed/accuracy balance
        self.model = WhisperModel("large-v2", device="cpu", compute_type="int8")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Enhanced language support for African languages
        self.supported_languages = {
            "en": "english",
            "yo": "yoruba",
            "ha": "hausa",
            "ig": "igbo",
            "sw": "swahili",
            "fr": "french",
            "ar": "arabic",
            "am": "amharic",
            "ak": "akan",
            "lg": "luganda",
            "sn": "shona",
            "zu": "zulu",
            "af": "afrikaans"
        }

        # Performance settings
        self.compute_type = "int8" if self.device == "cpu" else "float16"
        self.beam_size = 5
        self.best_of = 5

        logger.info(f"FastWhisperSTTAdapter using device: {self.device}, compute_type: {self.compute_type}")

    @classmethod
    async def get_instance(cls) -> 'FastWhisperSTTAdapter':
        """Get singleton instance of FastWhisperSTTAdapter."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._initialize()
        return cls._instance

    async def _initialize(self) -> None:
        """Initialize the Faster-Whisper model and language detector."""
        try:
            logger.info(f"Loading Faster-Whisper model ({self.model_size})...")

            # Load model with optimized settings
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None,
                self._load_model_sync
            )

            # Initialize language detector
            self.language_detector = await LanguageDetector.get_instance()

            logger.info("FastWhisperSTTAdapter initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize FastWhisperSTTAdapter: {e}")
            raise

    def _load_model_sync(self):
        """Synchronous model loading for thread execution."""
        return WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
            cpu_threads=4 if self.device == "cpu" else 0
        )

    async def transcribe(
        self,
        audio_data: Union[bytes, np.ndarray, str],
        language: Optional[str] = None,
        detect_language: bool = True,
        translate_to_english: bool = False
    ) -> Dict[str, Union[str, float, Dict]]:
        """
        Transcribe/translate audio to text with high performance.

        Args:
            audio_data: Audio data as bytes, numpy array, or file path
            language: Target language code (e.g., 'en', 'yo', 'ha')
            detect_language: Whether to detect language automatically
            translate_to_english: Whether to translate source language to English

        Returns:
            Dictionary containing transcription results
        """
        if self.model is None:
            await self._initialize()

        try:
            # Preprocess audio
            audio_array = await self._prepare_audio(audio_data)

            # Detect language if not specified
            detected_lang = None
            if detect_language and not language:
                detected_lang = await self.language_detector.detect_language(audio_array)
                language = detected_lang

            # Determine transcription settings
            source_language = self._map_language_code(language) if language else None
            task = "translate" if translate_to_english else "transcribe"

            # Run transcription
            loop = asyncio.get_event_loop()
            segments, info = await loop.run_in_executor(
                None,
                self._transcribe_sync,
                audio_array,
                source_language,
                task
            )

            # Process results
            text = " ".join([segment.text.strip() for segment in segments])

            return {
                "text": text,
                "language": info.language or language or detected_lang or "unknown",
                "confidence": info.language_probability,
                "segments": [
                    {
                        "text": segment.text,
                        "start": segment.start,
                        "end": segment.end,
                        "confidence": segment.avg_logprob
                    }
                    for segment in segments
                ],
                "detected_language": detected_lang,
                "processing_info": {
                    "model_size": self.model_size,
                    "device": self.device,
                    "compute_type": self.compute_type,
                    "duration": len(audio_array) / 16000.0
                }
            }

        except Exception as e:
            logger.error(f"Error in transcription: {e}")
            raise

    def _transcribe_sync(self, audio_array: np.ndarray, language: Optional[str], task: str):
        """Synchronous transcription using Faster-Whisper."""
        options = {
            "beam_size": self.beam_size,
            "best_of": self.best_of,
            "language": language,
            "task": task,
            "temperature": 0.0,  # Deterministic output
        }

        return self.model.transcribe(audio_array, **options)

    async def transcribe_and_translate(
        self,
        audio_data: Union[bytes, np.ndarray, str],
        source_language: Optional[str] = None
    ) -> Dict[str, Union[str, float, Dict]]:
        """
        Convenience method: transcribe from source language and translate to English.

        Args:
            audio_data: Audio data to process
            source_language: Source language code (auto-detect if None)

        Returns:
            Translation results
        """
        return await self.transcribe(
            audio_data,
            language=source_language,
            detect_language=True,
            translate_to_english=True
        )

    async def _prepare_audio(self, audio_data: Union[bytes, np.ndarray, str]) -> np.ndarray:
        """Prepare audio data for processing."""
        if isinstance(audio_data, str):
            # File path - load directly (Faster-Whisper handles this)
            return audio_data
        elif isinstance(audio_data, bytes):
            # Bytes data - convert to numpy array
            import io
            import soundfile as sf

            audio_array, sr = sf.read(io.BytesIO(audio_data))
            if sr != 16000:
                # Resample to 16kHz if needed
                import librosa
                audio_array = librosa.resample(audio_array, orig_sr=sr, target_sr=16000)
            return preprocess_audio(audio_array)
        elif isinstance(audio_data, np.ndarray):
            # Already numpy array
            return preprocess_audio(audio_data)
        else:
            raise ValueError(f"Unsupported audio data type: {type(audio_data)}")

    def _map_language_code(self, lang_code: str) -> str:
        """Map language code to Whisper-compatible format."""
        # Faster-Whisper uses ISO 639-1 codes
        mapping = {
            "yo": "yo",  # Yoruba
            "ha": "ha",  # Hausa
            "ig": "ig",  # Igbo
            "sw": "sw",  # Swahili
            "en": "en",  # English
            "fr": "fr",  # French
            "ar": "ar",  # Arabic
            "am": "am",  # Amharic
            "ak": "ak",  # Akan
            "lg": "lg",  # Luganda
            "sn": "sn",  # Shona
            "zu": "zu",  # Zulu
            "af": "af"   # Afrikaans
        }
        return mapping.get(lang_code, lang_code)

    async def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes and names."""
        return self.supported_languages.copy()

    async def get_performance_info(self) -> Dict[str, str]:
        """Get performance metrics for the current setup."""
        return {
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "beam_size": str(self.beam_size),
            "memory_usage": f"~{244 if self.model_size == 'small' else 74}MB"
        }

    async def health_check(self) -> Dict[str, Union[bool, str]]:
        """Perform health check on the STT system."""
        try:
            if self.model is None:
                return {"healthy": False, "error": "Model not loaded"}

            # Test with short silence
            test_audio = np.zeros(16000, dtype=np.float32)
            segments, info = self.model.transcribe(test_audio, language="en")

            return {
                "healthy": True,
                "model_size": self.model_size,
                "device": self.device,
                "compute_type": self.compute_type,
                "supported_languages": len(self.supported_languages),
                "memory_usage": f"~{244 if self.model_size == 'small' else 74}MB"
            }

        except Exception as e:
            return {"healthy": False, "error": str(e)}


async def demo():
    stt = await FastWhisperSTTAdapter.get_instance()

    # Transcribe Hausa audio (keeping original language)
    result = await stt.transcribe(r"C:\Users\hp\Desktop\super folder\PTT-20250721-WA0006 (1) (1).wav", language="ha")
    print("Hausa transcription:", result['text'])

    # Translate Hausa to English
    result = await stt.transcribe(r"C:\Users\hp\Desktop\super folder\PTT-20250721-WA0006 (1) (1).wav", translate_to_english=True)
    print("English translation:", result['text'])

    # Auto-detect language and translate to English
    result = await stt.transcribe_and_translate(r"C:\Users\hp\Desktop\super folder\PTT-20250721-WA0006 (1) (1).wav")
    print("Auto-detected + translated:", result['text'])

    # Performance info
    print(await stt.get_performance_info())

if __name__ == '__main__':
    asyncio.run(demo())