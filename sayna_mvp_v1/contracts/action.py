# contracts/action.py
from dataclasses import dataclass

from sayna_mvp_v1.support.errors_translator import WhatsappFailureReason


@dataclass(frozen=True)
class Messages:
    sender: str
    content: str
    is_from_me: bool
    time_stamp: str | None


@dataclass(frozen=True)
class ActionResult:
    success: bool
    data: list[Messages] | None
    failure_reason: WhatsappFailureReason | None
    matches: list[str] | None = None


@dataclass(frozen=True)
class ChatMatchResult:
    success: bool
    locator: str | None
    matches: list[str] | None
    failure_reason: WhatsappFailureReason | None


@dataclass(frozen=True)
class SearchResult:
    title: str
    locator: object