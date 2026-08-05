# contract/transcription.py

from sayna_mvp_v1.support.groq_errors_translator import FailureReason
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
    failure_reason: FailureReason | None
