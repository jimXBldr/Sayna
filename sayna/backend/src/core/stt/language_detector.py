"""
Language detection for SAYNA Voice OS.
Uses FastText for efficient language identification with African language focus.
"""


import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import fasttext


from sayna.backend.src.core.utils.audio import extract_text_features

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Language detector optimized for African languages."""

    _instance: Optional['LanguageDetector'] = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.model = None
        self.model_path = Path(r"C:\Users\hp\Desktop\super folder\Libary\SAYNA\lid.176.bin")
        self.supported_languages = {
            "en": "english",
            "yo": "yoruba",
            "ha": "hausa",
            "ig": "igbo",
            "sw": "swahili",
            "fr": "french",
            "ar": "arabic"
        }

        # Language code mappings (FastText uses different codes)
        self.fasttext_mappings = {
            "__label__en": "en",
            "__label__yo": "yo",
            "__label__ha": "ha",
            "__label__ig": "ig",
            "__label__sw": "sw",
            "__label__fr": "fr",
            "__label__ar": "ar"
        }

    @classmethod
    async def get_instance(cls) -> 'LanguageDetector':
        """Get singleton instance of LanguageDetector."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._initialize()
        return cls._instance

    async def _initialize(self) -> None:
        """Initialize the language detection model."""
        try:
            await self._ensure_model_downloaded()

            logger.info("Loading FastText language detection model...")
            loop = asyncio.get_event_loop()

            # Suppress FastText warnings
            fasttext.FastText.eprint = lambda x: None

            self.model = await loop.run_in_executor(
                None,
                fasttext.load_model,
                str(self.model_path)
            )

            logger.info("Language detector initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize language detector: {e}")
            # Fallback to rule-based detection
            self.model = None
            logger.warning("Using fallback language detection")

    async def _ensure_model_downloaded(self) -> None:
        """Ensure the FastText model is downloaded."""
        if self.model_path.exists():
            return

        logger.info("FastText model not found, downloading...")

        # Create directory
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: Download FastText language identification model
        # URL: https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
        # This should be done in the setup script

        if not self.model_path.exists():
            logger.warning("FastText model not available, using fallback detection")

    async def detect_language(
            self,
            text_or_audio: Union[str, np.ndarray],
            top_k: int = 3
    ) -> str:
        """
        Detect language from text or audio.

        Args:
            text_or_audio: Text string or audio array
            top_k: Number of top predictions to consider

        Returns:
            Detected language code (e.g., 'en', 'yo', 'ha')
        """
        try:
            # Convert audio to text if needed
            if isinstance(text_or_audio, np.ndarray):
                # Extract text features from audio (this is a placeholder)
                # In practice, you might use phonetic features or run STT first
                text = await self._audio_to_text_features(text_or_audio)
            else:
                text = text_or_audio

            if not text or len(text.strip()) < 3:
                return "en"  # Default to English for very short text

            # Use FastText model if available
            if self.model:
                return await self._detect_with_fasttext(text, top_k)
            else:
                return await self._detect_with_fallback(text)

        except Exception as e:
            logger.error(f"Error in language detection: {e}")
            return "en"  # Default fallback

    async def _detect_with_fasttext(self, text: str, top_k: int = 3) -> str:
        """Detect language using FastText model."""
        try:
            # Clean text for FastText
            cleaned_text = self._clean_text(text)

            # Run prediction in thread pool
            loop = asyncio.get_event_loop()
            predictions, confidences = await loop.run_in_executor(
                None,
                self.model.predict,
                cleaned_text,
                top_k
            )

            # Process results
            for pred, conf in zip(predictions, confidences):
                lang_code = self.fasttext_mappings.get(pred)
                if lang_code and conf > 0.3:  # Minimum confidence threshold
                    return lang_code

            # Fallback to English if no confident prediction
            return "en"

        except Exception as e:
            logger.error(f"FastText detection error: {e}")
            return await self._detect_with_fallback(text)

    async def _detect_with_fallback(self, text: str) -> str:
        """Fallback language detection using simple heuristics."""
        text_lower = text.lower()

        # Simple keyword-based detection for African languages
        yoruba_keywords = ["ṣe", "kí", "ni", "nígbà", "àti", "pé", "tí", "wọn", "sí", "fún"]
        hausa_keywords = ["da", "na", "ya", "ta", "su", "mu", "ku", "shi", "ita", "wa"]
        igbo_keywords = ["na", "nke", "ka", "nwere", "ga", "bụ", "nye", "site", "mgbe", "ọ"]
        swahili_keywords = ["na", "ya", "wa", "za", "kwa", "ni", "la", "cha", "ku", "tu"]

        # Count keyword matches
        scores = {
            "yo": sum(1 for word in yoruba_keywords if word in text_lower),
            "ha": sum(1 for word in hausa_keywords if word in text_lower),
            "ig": sum(1 for word in igbo_keywords if word in text_lower),
            "sw": sum(1 for word in swahili_keywords if word in text_lower),
        }

        # Check for special characters
        if any(char in text for char in "ṣẹọáéíóúàèìòùâêîôû"):
            scores["yo"] += 2

        # Arabic script detection
        if any('\u0600' <= char <= '\u06FF' for char in text):
            return "ar"

        # Find language with highest score
        max_score = max(scores.values())
        if max_score > 0:
            for lang, score in scores.items():
                if score == max_score:
                    return lang

        # Default to English
        return "en"

    def _clean_text(self, text: str) -> str:
        """Clean text for language detection."""
        # Remove extra whitespace and newlines
        text = " ".join(text.split())

        # Remove URLs and email addresses
        import re
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\S+@\S+', '', text)

        # Remove numbers and special characters for better language detection
        text = re.sub(r'[0-9]+', ' ', text)
        text = re.sub(r'[^\w\s\u0080-\uFFFF]', ' ', text)

        return text.strip()

    async def _audio_to_text_features(self, audio: np.ndarray) -> str:
        """Extract text-like features from audio for language detection."""
        # This is a placeholder implementation
        # In practice, you might extract phonetic features or use a lightweight STT
        try:
            features = extract_text_features(audio)
            # Convert audio features to a pseudo-text representation
            # This is a simplified approach - in production you'd want more sophisticated methods
            return " ".join([f"feature_{i}" for i in range(min(10, len(features)))])
        except Exception:
            return ""  # Return empty string if feature extraction fails

    async def get_language_info(self, lang_code: str) -> Dict[str, str]:
        """Get information about a language."""
        return {
            "code": lang_code,
            "name": self.supported_languages.get(lang_code, "Unknown"),
            "supported": lang_code in self.supported_languages
        }

    async def health_check(self) -> Dict[str, Union[bool, str, int]]:
        """Perform health check on language detection."""
        return {
            "healthy": True,
            "model_available": self.model is not None,
            "supported_languages": len(self.supported_languages),
            "fallback_active": self.model is None
        }



async def main():
    detector = await LanguageDetector.get_instance()
    lang = await detector.detect_language("My name is Jamiu")
    print(f"Detected Language: {lang}")

if __name__ == "__main__":
    asyncio.run(main())