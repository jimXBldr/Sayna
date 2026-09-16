# contracts/action.py
from dataclasses import dataclass
from sayna_mvp_v1.support.errors_translator import WhatsappFailureReason


@dataclass(frozen=True)
class MessageResult:
    success: bool
    content: list[str] | None
    failure_reason: WhatsappFailureReason | None


@dataclass(frozen=True)
class ActionResult:
    success: bool
    data: list[MessageResult] | None
    failure_reason: WhatsappFailureReason | None
    matches: list[str] | None


@dataclass(frozen=True)
class ChatMatchResult:
    success: bool
    locator: object | None
    matches: list[str] | None
    failure_reason: WhatsappFailureReason | None
