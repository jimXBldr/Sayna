# contract/transcription.py

from sayna_mvp_v1.support.errors_translator import GroqFailureReason
from dataclasses import dataclass


@dataclass
class TranscriptMetadata:
    no_speech_probability: float
    average_log_probability: float
    compression_ratio: float


@dataclass
class TranscriptionResult:
    success: bool
    transcript: str | None
    metadata: TranscriptMetadata | None
    failure_reason: GroqFailureReason | None
