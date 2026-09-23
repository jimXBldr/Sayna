from dataclasses import dataclass


@dataclass(frozen=True)
class ClarificationResult:
    success: bool | None
    updated_parameters: str
    failure_reason: Exception | None


@dataclass(frozen=True)
class ClarificationRequest:
    failure_reason: str
    parameters: list[str]
    new_parameter: str
