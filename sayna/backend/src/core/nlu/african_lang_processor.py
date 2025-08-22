"""
African Language Processor for SAYNA NLU.
Handles preprocessing and normalization for African languages.
"""

import logging
import re
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class AfricanLanguageProcessor:
    """Processor for African language text preprocessing and normalization."""

    def __init__(self):
        # Tone mark mappings for standardization
        self.tone_mappings = {
            # Yoruba tone marks
            "à": "a", "á": "a", "ā": "a",
            "è": "e", "é": "e", "ē": "e", "ẹ̀": "ẹ", "ẹ́": "ẹ", "ẹ̄": "ẹ",
            "ì": "i", "í": "i", "ī": "i",
            "ò": "o", "ó": "o", "ō": "o", "ọ̀": "ọ", "ọ́": "ọ", "ọ̄": "ọ",
            "ù": "u", "ú": "u", "ū": "u",
            "ǹ": "n", "ń": "n", "n̄": "n",
            # Uppercase versions
            "À": "A", "Á": "A", "Ā": "A",
            "È": "E", "É": "E", "Ē": "E", "Ẹ̀": "Ẹ", "Ẹ́": "Ẹ", "Ẹ̄": "Ẹ",
            "Ì": "I", "Í": "I", "Ī": "I",
            "Ò": "O", "Ó": "O", "Ō": "O", "Ọ̀": "Ọ", "Ọ́": "Ọ", "Ọ̄": "Ọ",
            "Ù": "U", "Ú": "U", "Ū": "U",
            "Ǹ": "N", "Ń": "N", "N̄": "N",
        }

        # Common contractions and abbreviations by language
        self.contractions = {
            "en": {
                "don't": "do not",
                "won't": "will not",
                "can't": "cannot",
                "n't": " not",
                "'re": " are",
                "'ve": " have",
                "'ll": " will",
                "'d": " would",
                "'m": " am",
            },
            "yo": {
                # Yoruba contractions (if any)
                "ló": "ni ó",
                "lá": "ni á",
                "lè": "lè",
            },
            "ha": {
                # Hausa contractions
                "ba'a": "ba a",
                "da'a": "da a",
            },
            "ig": {
                # Igbo contractions
                "n'": "na ",  # Common prefix
                "m'": "ma ",
            },
            "sw": {
                # Swahili contractions
                "si'yo": "si hayo",
                "ha'po": "hapo",
            }
        }

        # Stopwords by language (basic sets)
        self.stopwords = {
            "en": {
                "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
                "from", "up", "about", "into", "through", "during", "before", "after", "above", "below",
                "between", "among", "under", "over", "is", "am", "are", "was", "were", "be", "been",
                "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
                "may", "might", "must", "can", "this", "that", "these", "those", "i", "me", "my",
                "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
                "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it",
                "its", "itself", "they", "them", "their", "theirs", "themselves"
            },
            "yo": {
                "ni", "ti", "si", "bi", "ki", "fi", "ri", "wi", "di", "gi", "mi", "li", "pi", "hi",
                "àti", "tàbí", "ṣùgbọ́n", "nínú", "lórí", "ní", "sí", "fún", "ti", "pẹ̀lú", "láti",
                "sókè", "nípa", "sínú", "gbogbo", "àkókò", "ṣáájú", "lẹ́yìn", "lókè", "nísàlẹ̀",
                "láàárín", "láàmọ́", "abẹ́", "lórí", "jẹ́", "wa", "ṣe", "ní", "ti", "ó", "wá", "ṣe",
                "kò", "bá", "má", "lè", "yóò", "lè", "gbọdọ̀", "yi", "naa", "wọ̀nyí", "wọ́n", "mo",
                "mi", "wa", "àwa", "ẹ", "rẹ", "ara", "oun", "òun", "àwọn", "wọn", "wọ́n"
            },
            "ha": {
                "da", "na", "a", "ba", "ga", "ta", "sa", "ka", "fa", "ma", "la", "ra", "wa", "ya",
                "kuma", "ko", "amma", "cikin", "kan", "a", "ga", "don", "da", "daga", "sama", "game",
                "cikin", "duka", "lokaci", "kafin", "bayan", "sama", "kasa", "tsakanin", "cikin",
                "karkashin", "bisa", "ne", "ce", "ya", "ta", "sun", "mun", "kun", "shi", "ita", "su",
                "ni", "kai", "ke", "mu", "ku", "shi", "ita", "su"
            },
            "ig": {
                "na", "nke", "ma", "ka", "ga", "nye", "site", "maka", "ya", "nwere", "bu", "kwere",
                "mgbe", "tupu", "emesia", "elu", "ala", "otutu", "n'etiti", "n'okpuru", "n'elu",
                "bu", "di", "no", "nwere", "mere", "kwere", "ga", "gha", "nwere ike", "kwesiri",
                "a", "nke a", "ndi a", "ndi", "m", "gi", "anyi", "unu", "ya", "o", "ha", "onwe"
            },
            "sw": {
                "na", "ya", "wa", "za", "kwa", "ni", "la", "cha", "ku", "tu", "au", "lakini", "katika",
                "juu", "kwa", "ya", "kwa", "kutoka", "juu", "kuhusu", "ndani", "wote", "wakati",
                "kabla", "baada", "juu", "chini", "kati", "ndani", "chini", "juu", "ni", "kuwa",
                "ana", "wana", "una", "mna", "yeye", "wewe", "sisi", "nyinyi", "wao", "mimi", "wewe",
                "yeye", "sisi", "nyinyi", "wao"
            }
        }

        # Language-specific text patterns
        self.language_patterns = {
            "yo": {
                "word_boundary": r"\b(?=[aeioụọẹ])",  # Vowel-initial words are common
                "reduplication": r"(\w+)-\1",  # Yoruba reduplication pattern
            },
            "ha": {
                "word_boundary": r"\b(?=[aeiou])",
                "pharyngeal": r"[ʼ']",  # Pharyngeal consonant marker
            },
            "ig": {
                "word_boundary": r"\b(?=[aeiou])",
                "tone_prefix": r"^[àáâ]",  # Common tone prefixes
            },
            "sw": {
                "word_boundary": r"\b(?=[aeiou])",
                "noun_class": r"^(m|wa|mi|ya|ki|vi|n|zi|u|ku|pa|mu)",  # Swahili noun class prefixes
            }
        }

    async def preprocess_text(self, text: str, language: str = "en") -> str:
        """
        Preprocess text for the specified language.

        Args:
            text: Input text
            language: Language code

        Returns:
            Preprocessed text
        """
        try:
            if not text or not text.strip():
                return ""

            processed = text

            # Basic cleaning
            processed = self._clean_text(processed)

            # Language-specific preprocessing
            if language in ["yo", "ha", "ig", "sw"]:
                processed = await self._preprocess_african_language(processed, language)
            elif language == "en":
                processed = await self._preprocess_english(processed)

            # Final normalization
            processed = self._normalize_text(processed)

            return processed.strip()

        except Exception as e:
            logger.error(f"Error in text preprocessing: {e}")
            return text  # Return original text if preprocessing fails

    def _clean_text(self, text: str) -> str:
        """Basic text cleaning."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove control characters but keep basic punctuation
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # Normalize quotes
        text = re.sub(r'[""''`]', '"', text)

        # Normalize dashes
        text = re.sub(r'[–—]', '-', text)

        return text.strip()

    async def _preprocess_african_language(self, text: str, language: str) -> str:
        """Preprocess African language text."""
        processed = text

        # Handle contractions
        if language in self.contractions:
            for contraction, expansion in self.contractions[language].items():
                processed = re.sub(
                    re.escape(contraction),
                    expansion,
                    processed,
                    flags=re.IGNORECASE
                )

        # Language-specific processing
        if language == "yo":
            processed = await self._preprocess_yoruba(processed)
        elif language == "ha":
            processed = await self._preprocess_hausa(processed)
        elif language == "ig":
            processed = await self._preprocess_igbo(processed)
        elif language == "sw":
            processed = await self._preprocess_swahili(processed)

        return processed

    async def _preprocess_yoruba(self, text: str) -> str:
        """Preprocess Yoruba text."""
        processed = text

        # Normalize tone marks (optional - for tone-insensitive processing)
        # for toned, base in self.tone_mappings.items():
        #     processed = processed.replace(toned, base)

        # Handle common Yoruba contractions and elisions
        processed = re.sub(r'\bló\b', 'ni ó', processed)
        processed = re.sub(r'\blá\b', 'ni á', processed)
        processed = re.sub(r'\blóo\b', 'ni òun', processed)

        # Normalize double vowels
        processed = re.sub(r'([aeiouọẹ])\1+', r'\1', processed)

        return processed

    async def _preprocess_hausa(self, text: str) -> str:
        """Preprocess Hausa text."""
        processed = text

        # Handle Hausa apostrophes (glottal stops)
        processed = re.sub(r"'", "'", processed)  # Normalize apostrophe

        # Handle common Hausa prefixes and suffixes
        processed = re.sub(r'\bba-', 'ba ', processed)  # Separate negative prefix
        processed = re.sub(r'\bda-', 'da ', processed)  # Separate conjunction

        return processed

    async def _preprocess_igbo(self, text: str) -> str:
        """Preprocess Igbo text."""
        processed = text

        # Handle Igbo tone marks and dots
        processed = re.sub(r'([nṅ])([aeiou])', r'\1 \2', processed)  # Separate syllabic n

        # Handle common Igbo contractions
        processed = re.sub(r"\bn'", "na ", processed)  # Common prefix
        processed = re.sub(r"\bm'", "ma ", processed)  # Another common prefix

        return processed

    async def _preprocess_swahili(self, text: str) -> str:
        """Preprocess Swahili text."""
        processed = text

        # Handle Swahili apostrophes
        processed = re.sub(r"'", "'", processed)

        # Normalize common Swahili contractions
        processed = re.sub(r"si'yo", "si hayo", processed)
        processed = re.sub(r"ha'po", "hapo", processed)

        return processed

    async def _preprocess_english(self, text: str) -> str:
        """Preprocess English text."""
        processed = text

        # Handle English contractions
        for contraction, expansion in self.contractions["en"].items():
            pattern = re.escape(contraction)
            processed = re.sub(
                pattern,
                expansion,
                processed,
                flags=re.IGNORECASE
            )

        return processed

    def _normalize_text(self, text: str) -> str:
        """Final text normalization."""
        # Convert to lowercase for processing (preserving original case in entities)
        # processed = text.lower()

        # Remove extra punctuation at word boundaries
        processed = re.sub(r'\s+([.!?;,:])', r'\1', text)
        processed = re.sub(r'([.!?;,:])\s*([.!?;,:])', r'\1', processed)

        # Normalize whitespace
        processed = re.sub(r'\s+', ' ', processed)

        return processed.strip()

    def remove_stopwords(self, text: str, language: str = "en") -> str:
        """Remove stopwords from text."""
        if language not in self.stopwords:
            return text

        words = text.split()
        stopwords = self.stopwords[language]

        filtered_words = [
            word for word in words
            if word.lower() not in stopwords
        ]

        return " ".join(filtered_words)

    def extract_keywords(self, text: str, language: str = "en", min_length: int = 3) -> List[str]:
        """Extract keywords from text."""
        # Remove stopwords
        filtered_text = self.remove_stopwords(text, language)

        # Extract words
        words = re.findall(r'\b\w+\b', filtered_text.lower())

        # Filter by length and remove duplicates
        keywords = list(set([
            word for word in words
            if len(word) >= min_length and word.isalpha()
        ]))

        return sorted(keywords)

    def detect_language_features(self, text: str) -> Dict[str, float]:
        """Detect language-specific features in text."""
        features = {}

        # Character-based features
        features["yoruba_chars"] = len(re.findall(r'[ọẹṣ]', text.lower())) / max(1, len(text))
        features["arabic_chars"] = len(re.findall(r'[\u0600-\u06FF]', text)) / max(1, len(text))
        features["tone_marks"] = len(re.findall(r'[àáâèéêìíîòóôùúû]', text.lower())) / max(1, len(text))

        # Word-based features
        words = text.split()
        if words:
            features["avg_word_length"] = sum(len(word) for word in words) / len(words)
            features["long_words"] = len([w for w in words if len(w) > 8]) / len(words)
        else:
            features["avg_word_length"] = 0
            features["long_words"] = 0

        # Pattern-based features
        features["reduplication"] = len(re.findall(r'\b(\w+)-\1\b', text)) / max(1, len(words))
        features["apostrophes"] = text.count("'") / max(1, len(text))

        return features