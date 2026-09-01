# contract/llm.py

from dataclasses import dataclass
from sayna_mvp_v1.support.errors_translator import GroqFailureReason


@dataclass(frozen=True)
class LLMResult:
    success: bool
    content: str | None
    failure_reason: GroqFailureReason | None
