from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessedResult:
    success: bool
    processed_result: str | None
    failure_reason: Exception | None