"""
Slot extraction module for SAYNA NLU.
Extracts structured information from natural language text.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
import asyncio


from sayna.backend.src.core.nlu.african_lang_processor import AfricanLanguageProcessor

logger = logging.getLogger(__name__)


class SlotExtractor:
    """Advanced slot extraction for African languages."""

    def __init__(self):
        self.african_processor = AfricanLanguageProcessor()

        # Named entity patterns by language
        self.entity_patterns = {
            "PERSON": {
                "en": [
                    r"(?:for|to|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                    r"\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",

                ],
                "yo": [
                    r"(?:Ọgbẹni|Iyaafin|Baba|Mama)\s+([A-Z][a-z]+)",
                    r"fún\s+([A-Z][a-z]+)",
                    r"sí\s+([A-Z][a-z]+)"
                ],
                "ha": [
                    r"(?:Malam|Hajiya|Alhaji)\s+([A-Z][a-z]+)",
                    r"ga\s+([A-Z][a-z]+)",
                    r"don\s+([A-Z][a-z]+)"
                ],
                "ig": [
                    r"(?:Nna|Nne|Eze|Lolo)\s+([A-Z][a-z]+)",
                    r"nye\s+([A-Z][a-z]+)",
                    r"maka\s+([A-Z][a-z]+)"
                ],
                "sw": [
                    r"(?:Bwana|Mama|Mzee|Bi)\s+([A-Z][a-z]+)",
                    r"kwa\s+([A-Z][a-z]+)",
                    r"ya\s+([A-Z][a-z]+)"
                ]
            },

            "EMAIL": {
                "all": [r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"]
            },

            "PHONE": {
                "all": [
                    r"\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
                    r"\b\d{3}-\d{3}-\d{4}\b",
                    r"\b\d{10,15}\b"
                ]
            },

            "MONEY": {
                "en": [
                    r"[\$]\s?(\d+(?:,\d{3})*(?:\.\d{2})?)",
                    r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s?(?:dollars?|USD|cents?)"
                ],
                "yo": [
                    r"₦\s?(\d+(?:,\d{3})*(?:\.\d{2})?)",
                    r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s?naira"
                ],
                "ha": [
                    r"₦\s?(\d+(?:,\d{3})*(?:\.\d{2})?)",
                    r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s?naira"
                ],
                "ig": [
                    r"₦\s?(\d+(?:,\d{3})*(?:\.\d{2})?)",
                    r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s?naira"
                ],
                "sw": [
                    r"Tsh\s?(\d+(?:,\d{3})*(?:\.\d{2})?)",
                    r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s?shilingi"
                ]
            },

            "DATE": {
                "all": [
                    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
                    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}\b",
                    r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b"
                ],
                "en": [r"\b(?:today|tomorrow|yesterday|next week|last week)\b"],
                "yo": [r"\b(?:òní|ọ̀la|àná|ọ̀sẹ̀ tó ń bọ̀|ọ̀sẹ̀ tó kọjá)\b"],
                "ha": [r"\b(?:yau|gobe|jiya|mako mai zuwa|makon da ya wuce)\b"],
                "ig": [r"\b(?:taa|echi|ụnyaahụ|izu na-abịa|izu gara aga)\b"],
                "sw": [r"\b(?:leo|kesho|jana|wiki ijayo|wiki iliyopita)\b"]
            },

            "TIME": {
                "all": [
                    r"\b\d{1,2}:\d{2}(?::\d{2})?\s?(?:[AaPp][Mm])?\b",
                    r"\b\d{1,2}\s?(?:[AaPp][Mm])\b"
                ],
                "en": [r"\b(?:morning|afternoon|evening|night|noon|midnight)\b"],
                "yo": [r"\b(?:òwúrọ̀|ọ̀sán|àṣálẹ́|alẹ́|ọ̀gànjọ́)\b"],
                "ha": [r"\b(?:safiya|rana|yamma|dare|tsaka)\b"],
                "ig": [r"\b(?:ụtụtụ|ehihie|mgbede|abalị|etiti abalị)\b"],
                "sw": [r"\b(?:asubuhi|mchana|jioni|usiku|adhuhuri)\b"]
            }
        }

    async def extract_slots(
            self,
            text: str,
            language: str = "en",
            slot_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract slots from text.

        Args:
            text: Input text
            language: Language code
            slot_types: Specific slot types to extract (None for all)

        Returns:
            List of extracted slots
        """
        try:
            # Preprocess text
            processed_text = await self.african_processor.preprocess_text(text, language)

            slots = []
            extract_types = slot_types or list(self.entity_patterns.keys())

            for slot_type in extract_types:
                type_slots = await self._extract_slot_type(
                    processed_text, slot_type, language
                )
                slots.extend(type_slots)

            # Remove duplicates and sort by position
            slots = self._deduplicate_slots(slots)
            slots.sort(key=lambda x: x.get("start", 0))

            return slots

        except Exception as e:
            logger.error(f"Error in slot extraction: {e}")
            return []

    async def _extract_slot_type(
            self,
            text: str,
            slot_type: str,
            language: str
    ) -> List[Dict[str, Any]]:
        """Extract a specific type of slot from text."""
        slots = []

        if slot_type not in self.entity_patterns:
            return slots

        # Get patterns for this slot type and language
        type_patterns = self.entity_patterns[slot_type]

        # Use language-specific patterns if available, otherwise use 'all'
        if language in type_patterns:
            patterns = type_patterns[language]
        elif "all" in type_patterns:
            patterns = type_patterns["all"]
        else:
            patterns = type_patterns.get("en", [])

        # Extract matches for each pattern
        for pattern in patterns:
            try:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Use the first capturing group if available, otherwise the whole match
                    if match.groups():
                        value = match.group(1).strip()
                    else:
                        value = match.group(0).strip()

                    if value:  # Only add non-empty values
                        confidence = self._calculate_pattern_confidence(
                            pattern, value, slot_type
                        )

                        slots.append({
                            "type": slot_type,
                            "value": value,
                            "confidence": confidence,
                            "start": match.start(),
                            "end": match.end(),
                            "pattern": pattern
                        })

            except re.error as e:
                logger.warning(f"Invalid regex pattern {pattern}: {e}")
                continue

        return slots

    def _calculate_pattern_confidence(
            self,
            pattern: str,
            value: str,
            slot_type: str
    ) -> float:
        """Calculate confidence score for a pattern match."""
        base_confidence = 0.7

        # Boost confidence for specific patterns
        if slot_type == "EMAIL" and "@" in value:
            base_confidence = 0.95
        elif slot_type == "PHONE" and len(value.replace("-", "").replace(" ", "")) >= 10:
            base_confidence = 0.9
        elif slot_type == "MONEY" and any(char.isdigit() for char in value):
            base_confidence = 0.85
        elif slot_type == "PERSON" and value[0].isupper():
            base_confidence = 0.8

        # Adjust for pattern complexity
        pattern_complexity = len(pattern) / 50  # Normalize by typical pattern length
        complexity_bonus = min(0.15, pattern_complexity * 0.1)

        # Adjust for value length (reasonable entity lengths get bonus)
        if slot_type == "PERSON" and 2 <= len(value.split()) <= 4:
            base_confidence += 0.1
        elif slot_type == "EMAIL" and 5 <= len(value) <= 50:
            base_confidence += 0.05

        return min(0.99, base_confidence + complexity_bonus)

    def _deduplicate_slots(self, slots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate slots based on overlap and confidence."""
        if not slots:
            return slots

        # Sort by start position and confidence
        slots.sort(key=lambda x: (x.get("start", 0), -x.get("confidence", 0)))

        deduplicated = []
        for slot in slots:
            # Check for overlap with existing slots
            overlaps = False
            for existing in deduplicated:
                if self._slots_overlap(slot, existing):
                    # Keep the one with higher confidence
                    if slot.get("confidence", 0) > existing.get("confidence", 0):
                        deduplicated.remove(existing)
                        deduplicated.append(slot)
                    overlaps = True
                    break

            if not overlaps:
                deduplicated.append(slot)

        return deduplicated

    def _slots_overlap(self, slot1: Dict[str, Any], slot2: Dict[str, Any]) -> bool:
        """Check if two slots overlap in text position."""
        start1, end1 = slot1.get("start", 0), slot1.get("end", 0)
        start2, end2 = slot2.get("start", 0), slot2.get("end", 0)

        # Check for any overlap
        return not (end1 <= start2 or end2 <= start1)

    async def extract_contextual_slots(
            self,
            text: str,
            intent: str,
            language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Extract slots with context awareness based on intent."""
        try:
            # Get base slots
            base_slots = await self.extract_slots(text, language)

            # Apply intent-specific post-processing
            if intent == "create_invoice":
                return await self._process_invoice_context(base_slots, text, language)
            elif intent == "send_email":
                return await self._process_email_context(base_slots, text, language)
            elif intent == "send_whatsapp":
                return await self._process_whatsapp_context(base_slots, text, language)
            else:
                return base_slots

        except Exception as e:
            logger.error(f"Error in contextual slot extraction: {e}")
            return []

    async def _process_invoice_context(
            self,
            slots: List[Dict[str, Any]],
            text: str,
            language: str
    ) -> List[Dict[str, Any]]:
        """Process slots in the context of invoice creation."""
        processed_slots = slots.copy()

        # Look for recipient indicators
        recipient_indicators = {
            "en": ["for", "to", "bill"],
            "yo": ["fún", "sí"],
            "ha": ["ga", "don"],
            "ig": ["nye", "maka"],
            "sw": ["kwa", "ya"]
        }

        indicators = recipient_indicators.get(language, recipient_indicators["en"])

        # Enhance PERSON slots that appear after recipient indicators
        for slot in processed_slots:
            if slot["type"] == "PERSON":
                # Check if person appears after recipient indicator
                person_start = slot.get("start", 0)
                text_before = text[:person_start].lower()

                for indicator in indicators:
                    if indicator in text_before[-20:]:  # Check last 20 characters
                        slot["role"] = "recipient"
                        slot["confidence"] = min(0.95, slot.get("confidence", 0) + 0.1)
                        break

        # Add document type if missing
        if not any(s["type"] == "DOCUMENT_TYPE" for s in processed_slots):
            doc_keywords = {
                "en": ["invoice", "bill", "receipt"],
                "yo": ["ìwé ìsanwo", "àkọsílẹ̀ owó"],
                "ha": ["lissafi", "takarda kuɗi"],
                "ig": ["akwụkwọ ụgwọ", "akwụkwọ ego"],
                "sw": ["ankara", "bili"]
            }

            keywords = doc_keywords.get(language, doc_keywords["en"])
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    processed_slots.append({
                        "type": "DOCUMENT_TYPE",
                        "value": "invoice",
                        "confidence": 0.9,
                        "start": text.lower().find(keyword.lower()),
                        "end": text.lower().find(keyword.lower()) + len(keyword),
                        "inferred": True
                    })
                    break

        return processed_slots

    async def _process_email_context(
            self,
            slots: List[Dict[str, Any]],
            text: str,
            language: str
    ) -> List[Dict[str, Any]]:
        """Process slots in the context of email sending."""
        processed_slots = slots.copy()

        # Ensure we have a recipient
        has_email = any(s["type"] == "EMAIL" for s in processed_slots)
        has_person = any(s["type"] == "PERSON" for s in processed_slots)

        if not has_email and not has_person:
            # Try to infer recipient from context
            recipient_patterns = {
                "en": [r"send.*to\s+([A-Za-z]+)", r"email\s+([A-Za-z]+)"],
                "yo": [r"rán.*sí\s+([A-Za-z]+)", r"fi.*imeeli.*ranṣẹ.*sí\s+([A-Za-z]+)"],
                "ha": [r"aika.*ga\s+([A-Za-z]+)", r"tura.*wa\s+([A-Za-z]+)"],
                "ig": [r"ziga.*([A-Za-z]+)", r"zipụ.*nye\s+([A-Za-z]+)"],
                "sw": [r"tuma.*kwa\s+([A-Za-z]+)", r"peleka.*([A-Za-z]+)"]
            }

            patterns = recipient_patterns.get(language, recipient_patterns["en"])
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    processed_slots.append({
                        "type": "PERSON",
                        "value": matches[0],
                        "confidence": 0.7,
                        "start": text.lower().find(matches[0].lower()),
                        "end": text.lower().find(matches[0].lower()) + len(matches[0]),
                        "role": "recipient",
                        "inferred": True
                    })
                    break

        return processed_slots

    async def _process_whatsapp_context(
            self,
            slots: List[Dict[str, Any]],
            text: str,
            language: str
    ) -> List[Dict[str, Any]]:
        """Process slots in the context of WhatsApp messaging."""
        processed_slots = slots.copy()

        # Mark phone numbers as WhatsApp contacts
        for slot in processed_slots:
            if slot["type"] == "PHONE":
                slot["platform"] = "whatsapp"
                slot["confidence"] = min(0.95, slot.get("confidence", 0) + 0.05)

        # Look for notification keywords
        notification_keywords = {
            "en": ["notify", "tell", "inform", "let know"],
            "yo": ["sọ fún", "kí n mọ̀", "fi ọ́ ránṣẹ́"],
            "ha": ["sanar da", "gaya wa", "fadawa"],
            "ig": ["gwa", "kpọọ", "zie ozi"],
            "sw": ["julisha", "arifu", "taarifa"]
        }

        keywords = notification_keywords.get(language, notification_keywords["en"])
        for keyword in keywords:
            if keyword.lower() in text.lower():
                # This indicates a notification rather than a direct message
                for slot in processed_slots:
                    if slot["type"] in ["PERSON", "PHONE"]:
                        slot["message_type"] = "notification"
                break

        return processed_slots

    async def validate_slots(
            self,
            slots: List[Dict[str, Any]],
            intent: str
    ) -> Dict[str, Any]:
        """Validate extracted slots against intent requirements."""
        validation_result = {
            "valid": True,
            "missing_required": [],
            "invalid_slots": [],
            "warnings": []
        }

        # Define required slots by intent
        required_slots = {
            "create_invoice": ["PERSON"],
            "send_email": ["PERSON", "EMAIL"],  # At least one
            "send_whatsapp": ["PERSON", "PHONE"],  # At least one
        }

        if intent in required_slots:
            required = required_slots[intent]

            # Check for alternative requirements (OR logic)
            if intent == "send_email":
                has_person = any(s["type"] == "PERSON" for s in slots)
                has_email = any(s["type"] == "EMAIL" for s in slots)
                if not (has_person or has_email):
                    validation_result["missing_required"].append("PERSON or EMAIL")
                    validation_result["valid"] = False

            elif intent == "send_whatsapp":
                has_person = any(s["type"] == "PERSON" for s in slots)
                has_phone = any(s["type"] == "PHONE" for s in slots)
                if not (has_person or has_phone):
                    validation_result["missing_required"].append("PERSON or PHONE")
                    validation_result["valid"] = False

            else:
                # Standard AND logic for other intents
                found_types = {s["type"] for s in slots}
                missing = [req for req in required if req not in found_types]
                if missing:
                    validation_result["missing_required"].extend(missing)
                    validation_result["valid"] = False

        # Check slot confidence levels
        low_confidence_slots = [
            s for s in slots if s.get("confidence", 0) < 0.5
        ]
        if low_confidence_slots:
            validation_result["warnings"].append(
                f"{len(low_confidence_slots)} slots have low confidence"
            )

        # Validate specific slot formats
        for slot in slots:
            if slot["type"] == "EMAIL":
                if "@" not in slot["value"] or "." not in slot["value"]:
                    validation_result["invalid_slots"].append(slot)
                    validation_result["valid"] = False

            elif slot["type"] == "PHONE":
                # Remove formatting and check if it's mostly digits
                clean_phone = re.sub(r'[^\d]', '', slot["value"])
                if len(clean_phone) < 7:  # Minimum reasonable phone number length
                    validation_result["invalid_slots"].append(slot)
                    validation_result["warnings"].append(
                        f"Phone number '{slot['value']}' may be too short"
                    )

        return validation_result


async def main():
    se = SlotExtractor()

    samples = [
        ("Create invoice for Ada ₦10,000 tomorrow at 2 pm", "en"),
        ("Dá ìwé ìsanwo fún Tunde ₦5,000 òní ní 10:30", "yo"),
        ("Tura WhatsApp zuwa +2348123456789", "ha"),
        ("Send email to john@example.com", "en"),
    ]

    for text, lang in samples:
        slots = await se.extract_slots(text, language=lang)
        print(f"\n{lang.upper()}  '{text}'")
        for s in slots:
            print(f"  {s['type']:10} {s['value']:<20} conf={s['confidence']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())