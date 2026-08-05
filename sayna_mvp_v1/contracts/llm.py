# contract/llm.py

from dataclasses import dataclass
from sayna_mvp_v1.support.groq_errors_translator import FailureReason


@dataclass(frozen=True)
class LLMResult:
    success: bool
    content: str | None
    failure_reason: FailureReason | None
