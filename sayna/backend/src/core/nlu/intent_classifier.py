"""
Natural Language Understanding (NLU) Intent Classifier for SAYNA.
Handles intent classification and slot extraction for African languages.
"""

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
from transformers import AutoTokenizer, pipeline

from sayna.backend.src.core.nlu.african_lang_processor import AfricanLanguageProcessor

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Intent classifier with African language support."""

    _instance: Optional['IntentClassifier'] = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.classifier_pipeline = None
        self.rule_based_patterns = {}
        self.african_processor = None

        # Intent taxonomy
        self.intent_categories = {
            "productivity": ["create_invoice", "send_email", "schedule_meeting", "create_document"],
            "communication": ["send_message", "make_call", "send_notification", "send_whatsapp"],
            "finance": ["create_invoice", "process_payment", "check_balance", "generate_report"],
            "system": ["help", "settings", "status", "cancel"]
        }

        # Slot types
        self.slot_types = [
            "PERSON", "EMAIL", "DATE", "TIME", "MONEY", "ORGANIZATION",
            "PHONE", "DOCUMENT_TYPE", "ACTION", "RECIPIENT"
        ]

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    @classmethod
    async def get_instance(cls) -> 'IntentClassifier':
        """Get singleton instance of IntentClassifier."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._initialize()
        return cls._instance

    async def _initialize(self) -> None:
        """Initialize the intent classifier."""
        try:
            logger.info("Initializing Intent Classifier...")

            # Initialize African language processor
            self.african_processor = AfricanLanguageProcessor()

            # Load rule-based patterns
            await self._load_rule_patterns()

            # Try to load transformer model (fallback to rule-based if not available)
            try:
                await self._load_transformer_model()
            except Exception as e:
                logger.warning(f"Could not load transformer model: {e}")
                logger.info("Using rule-based classification only")

            logger.info("Intent Classifier initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Intent Classifier: {e}")
            raise

    async def _load_transformer_model(self) -> None:
        """Load transformer model for intent classification."""
        # For production, you would fine-tune a model on African languages
        # For demo, we'll use a general multilingual model

        model_name = "microsoft/DialoGPT-medium"  # Placeholder - would use custom model

        try:
            loop = asyncio.get_event_loop()

            # Load tokenizer and model
            self.tokenizer = await loop.run_in_executor(
                None,
                AutoTokenizer.from_pretrained,
                model_name
            )

            # For demo purposes, we'll use a classification pipeline
            # In production, you'd use a properly trained intent classification model
            self.classifier_pipeline = await loop.run_in_executor(
                None,
                pipeline,
                "text-classification",
                model="facebook/bart-large-mnli",  # Zero-shot classification
                device=0 if self.device == "cuda" else -1
            )

            logger.info(f"Loaded transformer model: {model_name}")

        except Exception as e:
            logger.error(f"Error loading transformer model: {e}")
            raise

    async def _load_rule_patterns(self) -> None:
        """Load rule-based intent patterns."""
        patterns_file = Path("data/datasets/intent_patterns.json")

        if patterns_file.exists():
            with open(patterns_file, 'r', encoding='utf-8') as f:
                self.rule_based_patterns = json.load(f)
        else:
            # Default patterns for demo
            self.rule_based_patterns = {
                "create_invoice": {
                    "en": [r"create.*invoice", r"make.*invoice", r"generate.*bill"],
                    "yo": [r"ṣe.*ìwé.*ìsanwo", r"dá.*ìwé.*owó", r"ṣe.*àkọsílẹ.*owó", r"dá.*ìwé.*ìsanwo.*fún.*"],
                    "ha": [r"yi.*lissafi", r"samar.*da.*lissafi", r"rubuta.*lissafi"],
                    "ig": [r"mee.*akwụkwọ.*ụgwọ", r"dee.*akwụkwọ.*ego", r"rụọ.*akwụkwọ"],
                    "sw": [r"tengeneza.*ankara", r"fanya.*hesabu", r"andika.*bili"]
                },
                "send_email": {
                    "en": [r"send.*email", r"email.*to", r"send.*message"],
                    "yo": [r"fi.*imeeli.*ranṣẹ", r"rán.*imeeli", r"fi.*ifiranṣẹ.*ranṣẹ"],
                    "ha": [r"aika.*imel", r"tura.*saƙo", r"aika.*wasiƙa"],
                    "ig": [r"ziga.*email", r"zipụ.*ozi", r"ziga.*akwụkwọ"],
                    "sw": [r"tuma.*barua.*pepe", r"peleka.*email", r"tuma.*ujumbe"]
                },
                "send_whatsapp": {
                    "en": [r"whatsapp", r"send.*whatsapp", r"notify.*whatsapp"],
                    "yo": [r"whatsapp", r"rán.*sí.*whatsapp", r"fi.*whatsapp.*ranṣẹ"],
                    "ha": [r"whatsapp", r"aika.*whatsapp", r"tura.*whatsapp"],
                    "ig": [r"whatsapp", r"ziga.*whatsapp", r"kpọọ.*whatsapp"],
                    "sw": [r"whatsapp", r"tuma.*whatsapp", r"piga.*whatsapp"]
                }
            }

    async def classify_intent(
            self,
            text: str,
            language: str = "en",
            context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classify intent from text.

        Args:
            text: Input text
            language: Language code
            context: Optional context information

        Returns:
            Dictionary with intent classification results
        """
        try:
            # Preprocess text for the specific language
            processed_text = await self.african_processor.preprocess_text(text, language)

            # Try transformer-based classification first
            if self.classifier_pipeline:
                transformer_result = await self._classify_with_transformer(processed_text)
            else:
                transformer_result = None

            # Rule-based classification
            rule_result = await self._classify_with_rules(processed_text, language)

            # Combine results (prioritize transformer if available and confident)
            if (transformer_result and
                    transformer_result.get("confidence", 0) > 0.7):
                final_intent = transformer_result["intent"]
                confidence = transformer_result["confidence"]
                method = "transformer"
            else:
                final_intent = rule_result["intent"]
                confidence = rule_result["confidence"]
                method = "rule-based"

            return {
                "intent": final_intent,
                "confidence": confidence,
                "method": method,
                "language": language,
                "original_text": text,
                "processed_text": processed_text,
                "alternatives": [
                    transformer_result if transformer_result else rule_result,
                    rule_result if transformer_result else None
                ]
            }

        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "method": "fallback",
                "error": str(e)
            }

    async def _classify_with_transformer(self, text: str) -> Optional[Dict[str, Any]]:
        """Classify intent using transformer model."""
        try:
            # Define candidate labels for zero-shot classification
            candidate_labels = [
                "create invoice", "send email", "send message",
                "send whatsapp notification", "make payment",
                "schedule meeting", "get help", "cancel action"
            ]

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.classifier_pipeline,
                text,
                candidate_labels
            )

            if result and result["scores"]:
                # Map back to our intent names
                intent_mapping = {
                    "create invoice": "create_invoice",
                    "send email": "send_email",
                    "send message": "send_message",
                    "send whatsapp notification": "send_whatsapp",
                    "make payment": "process_payment",
                    "schedule meeting": "schedule_meeting",
                    "get help": "help",
                    "cancel action": "cancel"
                }

                top_label = result["labels"][0]
                confidence = result["scores"][0]

                return {
                    "intent": intent_mapping.get(top_label, "unknown"),
                    "confidence": confidence,
                    "raw_result": result
                }

        except Exception as e:
            logger.error(f"Transformer classification error: {e}")
            return None

    async def _classify_with_rules(self, text: str, language: str) -> Dict[str, Any]:
        """Classify intent using rule-based patterns."""
        text_lower = text.lower()
        best_match = {"intent": "unknown", "confidence": 0.0, "matches": []}

        for intent, lang_patterns in self.rule_based_patterns.items():
            patterns = lang_patterns.get(language, [])

            for pattern in patterns:
                try:
                    matches = re.findall(pattern, text_lower, re.IGNORECASE)
                    if matches:
                        # Calculate confidence based on pattern specificity and coverage
                        confidence = min(0.9, 0.3 + len(matches) * 0.2 + len(pattern) / len(text))

                        if confidence > best_match["confidence"]:
                            best_match = {
                                "intent": intent,
                                "confidence": confidence,
                                "matches": matches,
                                "pattern": pattern
                            }
                except re.error as e:
                    logger.warning(f"Invalid regex pattern {pattern}: {e}")
                    continue

        return best_match

    async def extract_slots(
            self,
            text: str,
            intent: str,
            language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Extract slots/entities from text based on intent.

        Args:
            text: Input text
            intent: Detected intent
            language: Language code

        Returns:
            List of extracted slots
        """
        try:
            slots = []

            # Process with African language processor
            processed_text = await self.african_processor.preprocess_text(text, language)

            # Intent-specific slot extraction
            if intent == "create_invoice":
                slots.extend(await self._extract_invoice_slots(processed_text, language))
            elif intent == "send_email":
                slots.extend(await self._extract_email_slots(processed_text, language))
            elif intent == "send_whatsapp":
                slots.extend(await self._extract_whatsapp_slots(processed_text, language))

            # General entity extraction
            general_slots = await self._extract_general_entities(processed_text, language)
            slots.extend(general_slots)

            return slots

        except Exception as e:
            logger.error(f"Error in slot extraction: {e}")
            return []

    async def _extract_invoice_slots(self, text: str, language: str) -> List[Dict[str, Any]]:
        """Extract slots specific to invoice creation."""
        slots = []

        # Person/recipient patterns by language
        person_patterns = {
            "en": [r"for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", r"to\s+([A-Z][a-z]+)"],
            "yo": [r"fún\s+([A-Z][a-z]+)", r"sí\s+([A-Z][a-z]+)"],
            "ha": [r"ga\s+([A-Z][a-z]+)", r"don\s+([A-Z][a-z]+)"],
            "ig": [r"nye\s+([A-Z][a-z]+)", r"maka\s+([A-Z][a-z]+)"],
            "sw": [r"kwa\s+([A-Z][a-z]+)", r"ya\s+([A-Z][a-z]+)"]
        }

        patterns = person_patterns.get(language, person_patterns["en"])
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                slots.append({
                    "type": "PERSON",
                    "value": match.strip(),
                    "confidence": 0.8,
                    "start": text.find(match),
                    "end": text.find(match) + len(match)
                })

        # Amount/money patterns (simple)
        money_pattern = r"[\$£€₦]?(\d+(?:[.,]\d{2})?)"
        money_matches = re.findall(money_pattern, text)
        for match in money_matches:
            slots.append({
                "type": "MONEY",
                "value": match,
                "confidence": 0.9,
                "start": text.find(match),
                "end": text.find(match) + len(match)
            })

        return slots

    async def _extract_email_slots(self, text: str, language: str) -> List[Dict[str, Any]]:
        """Extract slots specific to email sending."""
        slots = []

        # Email address pattern
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        email_matches = re.findall(email_pattern, text)
        for match in email_matches:
            slots.append({
                "type": "EMAIL",
                "value": match,
                "confidence": 0.95,
                "start": text.find(match),
                "end": text.find(match) + len(match)
            })

        return slots

    async def _extract_whatsapp_slots(self, text: str, language: str) -> List[Dict[str, Any]]:
        """Extract slots specific to WhatsApp messaging."""
        slots = []

        # Phone number patterns
        phone_patterns = [
            r"\+\d{1,3}\s?\d{3,14}",  # International format
            r"\b\d{10,15}\b"  # Simple digit sequence
        ]

        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                slots.append({
                    "type": "PHONE",
                    "value": match.strip(),
                    "confidence": 0.8,
                    "start": text.find(match),
                    "end": text.find(match) + len(match)
                })

        return slots

    async def _extract_general_entities(self, text: str, language: str) -> List[Dict[str, Any]]:
        """Extract general entities from text."""
        slots = []

        # Date patterns (simple)
        date_patterns = [
            r"\d{1,2}/\d{1,2}/\d{2,4}",
            r"\d{1,2}-\d{1,2}-\d{2,4}",
            r"today|tomorrow|yesterday"
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                slots.append({
                    "type": "DATE",
                    "value": match,
                    "confidence": 0.7,
                    "start": text.find(match),
                    "end": text.find(match) + len(match)
                })

        # Time patterns
        time_patterns = [
            r"\d{1,2}:\d{2}\s?(?:AM|PM)?",
            r"\d{1,2}\s?(?:AM|PM)"
        ]

        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                slots.append({
                    "type": "TIME",
                    "value": match,
                    "confidence": 0.8,
                    "start": text.find(match),
                    "end": text.find(match) + len(match)
                })

        return slots

    async def get_intent_info(self, intent: str) -> Dict[str, Any]:
        """Get information about a specific intent."""
        for category, intents in self.intent_categories.items():
            if intent in intents:
                return {
                    "intent": intent,
                    "category": category,
                    "description": f"Intent for {intent.replace('_', ' ')}",
                    "supported": True
                }

        return {
            "intent": intent,
            "category": "unknown",
            "description": "Unknown intent",
            "supported": False
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the NLU system."""
        return {
            "healthy": True,
            "transformer_available": self.classifier_pipeline is not None,
            "rule_patterns_loaded": len(self.rule_based_patterns) > 0,
            "supported_intents": sum(len(intents) for intents in self.intent_categories.values()),
            "supported_languages": ["en", "yo", "ha", "ig", "sw"]
        }



async def _demo():
    clf = await IntentClassifier.get_instance()

    examples = [
        ("Dá ìwé ìsanwo fún Musa ₦5000", "yo"),
        ("Send email to john@example.com", "en"),
        ("Tura WhatsApp zuwa +2348123456789", "ha"),
    ]

    for text, lang in examples:
        intent = await clf.classify_intent(text, language=lang)
        slots  = await clf.extract_slots(text, intent["intent"], language=lang)
        print(f"\n{lang.upper()}  '{text}' → intent={intent['intent']}  slots={slots}")

if __name__ == "__main__":
    asyncio.run(_demo())