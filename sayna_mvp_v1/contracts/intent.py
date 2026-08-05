# contract/intent.py
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StructuredRequest:
    intent: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class IntentResult:
    success: bool
    structured_request: StructuredRequest | None
    failure_reason: Exception | None
