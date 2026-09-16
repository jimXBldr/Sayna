from dataclasses import dataclass

@dataclass(frozen=True)
class ProcessedResult:
    success: bool
    