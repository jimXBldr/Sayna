"""
Orchestrator for SAYNA Voice OS.
Coordinates the complete voice interaction pipeline.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional, List

from src.core.nlu.intent_classifier import IntentClassifier
from src.core.orchestration.capability_registry import CapabilityRegistry
from src.core.stt.whisper_adapter import WhisperSTTAdapter
from src.core.tts.espnet_adapter import ESPnetTTSAdapter
from src.utils.audio import validate_audio_file

logger = logging.getLogger(__name__)


class VoiceOrchestrator:
    """Main orchestrator for voice interactions."""

    _instance: Optional['VoiceOrchestrator'] = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.stt = None
        self.nlu = None
        self.tts = None
        self.capability_registry = None

    @classmethod
    async def get_instance(cls) -> 'VoiceOrchestrator':
        """Get singleton instance of VoiceOrchestrator."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._initialize()
        return cls._instance

    async def _initialize(self) -> None:
        """Initialize the orchestrator components."""
        try:
            logger.info("Initializing Voice Orchestrator...")

            # Initialize components
            self.stt = await WhisperSTTAdapter.get_instance()
            self.nlu = await IntentClassifier.get_instance()
            self.tts = await ESPnetTTSAdapter.get_instance()
            self.capability_registry = CapabilityRegistry()

            await self.capability_registry.load_capabilities()

            logger.info("Voice Orchestrator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Voice Orchestrator: {e}")
            raise

    async def process_voice_input(
            self,
            audio_data: bytes,
            preferred_language: Optional[str] = None,
            session_id: Optional[str] = None,
            streaming: bool = False
    ) -> Dict[str, Any]:
        """
        Process voice input through the complete pipeline.

        Args:
            audio_data: Audio data in bytes
            preferred_language: Preferred language code
            session_id: Session identifier
            streaming: Whether this is a streaming request

        Returns:
            Dictionary with processing results
        """
        start_time = time.time()

        try:
            # Validate audio
            if not validate_audio_file(audio_data):
                raise ValueError("Invalid audio data format")

            # Step 1: Speech-to-Text
            stt_result = await self.stt.transcribe(
                audio_data,
                language=preferred_language,
                detect_language=True
            )

            transcript = stt_result["text"]
            detected_language = stt_result["language"]

            # Step 2: Natural Language Understanding
            nlu_result = await self.nlu.classify_intent(
                transcript,
                language=detected_language
            )

            intent = nlu_result["intent"]
            confidence = nlu_result["confidence"]

            # Step 3: Slot Extraction
            slots = await self.nlu.extract_slots(
                transcript,
                intent,
                detected_language
            )

            # Step 4: Capability Discovery
            capabilities = await self.capability_registry.find_capabilities(
                intent=intent,
                language=detected_language
            )

            if not capabilities:
                raise ValueError(f"No capabilities found for intent: {intent}")

            # Step 5: Action Planning
            actions = []
            for capability in capabilities:
                action = capability.actions.get(intent)
                if action:
                    actions.append({
                        "capability": capability.id,
                        "action": intent,
                        "parameters": self._map_parameters(action.parameters, slots),
                        "connector": capability.connector
                    })

            # Step 6: Generate TTS Response
            tts_response = None
            if not streaming:
                response_text = self._generate_response_text(intent, actions)
                tts_audio = await self.tts.synthesize(
                    response_text,
                    language=detected_language
                )
                tts_response = {
                    "text": response_text,
                    "audio": tts_audio
                }

            processing_time_ms = int((time.time() - start_time) * 1000)

            return {
                "session_id": session_id or "unknown",
                "transcript": transcript,
                "detected_language": detected_language,
                "intent": intent,
                "confidence": confidence,
                "entities": slots,
                "capabilities": [cap.id for cap in capabilities],
                "actions": actions,
                "response_text": tts_response["text"] if tts_response else None,
                "response_audio": tts_response["audio"] if tts_response else None,
                "processing_time_ms": processing_time_ms,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            return {
                "session_id": session_id or "unknown",
                "error": str(e),
                "success": False,
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }

    async def process_text_input(
            self,
            text: str,
            language: str = "en",
            session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process text input through the NLU and orchestration pipeline.

        Args:
            text: Input text
            language: Language code
            session_id: Session identifier

        Returns:
            Dictionary with processing results
        """
        start_time = time.time()

        try:
            # Step 1: Natural Language Understanding
            nlu_result = await self.nlu.classify_intent(text, language)
            intent = nlu_result["intent"]

            # Step 2: Slot Extraction
            slots = await self.nlu.extract_slots(text, intent, language)

            # Step 3: Capability Discovery
            capabilities = await self.capability_registry.find_capabilities(
                intent=intent,
                language=language
            )

            if not capabilities:
                raise ValueError(f"No capabilities found for intent: {intent}")

            # Step 4: Action Planning
            actions = []
            for capability in capabilities:
                action = capability.actions.get(intent)
                if action:
                    actions.append({
                        "capability": capability.id,
                        "action": intent,
                        "parameters": self._map_parameters(action.parameters, slots),
                        "connector": capability.connector
                    })

            processing_time_ms = int((time.time() - start_time) * 1000)

            return {
                "session_id": session_id or "unknown",
                "text": text,
                "language": language,
                "intent": intent,
                "entities": slots,
                "capabilities": [cap.id for cap in capabilities],
                "actions": actions,
                "processing_time_ms": processing_time_ms,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error processing text input: {e}")
            return {
                "session_id": session_id or "unknown",
                "error": str(e),
                "success": False,
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }

    def _map_parameters(
            self,
            parameters: List[Dict[str, Any]],
            slots: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Map extracted slots to action parameters."""
        param_map = {}

        for param in parameters:
            param_name = param["name"]
            param_type = param["type"]

            # Find matching slot
            matching_slots = [
                slot for slot in slots
                if slot["type"].lower() == param_type.lower()
            ]

            if matching_slots:
                param_map[param_name] = matching_slots[0]["value"]
            elif not param["required"]:
                param_map[param_name] = None
            else:
                raise ValueError(f"Required parameter {param_name} not found")

        return param_map

    def _generate_response_text(
            self,
            intent: str,
            actions: List[Dict[str, Any]]
    ) -> str:
        """Generate natural language response text for an intent."""
        responses = {
            "create_invoice": "I've created an invoice for {recipient} for the amount of {amount}.",
            "send_email": "I've sent an email to {recipient} with the subject '{subject}'.",
            "send_whatsapp": "I've sent a WhatsApp message to {recipient}."
        }

        template = responses.get(intent, "I've completed the requested action.")

        # Extract parameters from first action
        if actions and actions[0].get("parameters"):
            params = actions[0]["parameters"]
            try:
                return template.format(**params)
            except KeyError:
                pass

        return template

    async def get_available_capabilities(self) -> List[Dict[str, Any]]:
        """Get list of available capabilities with metadata."""
        capabilities = await self.capability_registry.list_capabilities()
        return [
            {
                "id": cap.id,
                "name": cap.name,
                "description": cap.description,
                "category": cap.category,
                "actions": list(cap.actions.keys())
            }
            for cap in capabilities
        ]

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the orchestrator."""
        checks = {
            "stt": await self.stt.health_check(),
            "nlu": await self.nlu.health_check(),
            "tts": await self.tts.health_check(),
            "capabilities": await self.capability_registry.health_check()
        }

        healthy = all(
            check.get("healthy", False)
            for check in checks.values()
        )

        return {
            "healthy": healthy,
            "components": checks,
            "status": "operational" if healthy else "degraded"
        }