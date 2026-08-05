# contracts/action.py
from dataclasses import dataclass


@dataclass(frozen=True)
class ActionResult:
    success: bool
    data: object | None
    failure_reason: Exception | None