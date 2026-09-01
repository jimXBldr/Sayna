# support/errors_translators.py

from enum import Enum
from groq import (AuthenticationError, BadRequestError,
                  RateLimitError, APITimeoutError,
                  InternalServerError, PermissionDeniedError,
                  APIConnectionError, UnprocessableEntityError, APIStatusError)


class GroqFailureReason(Enum):
    AUTHENTICATION_FAILED = "authentication_failed"
    RATE_LIMITED = "rate_limited"
    REQUEST_TIMEOUT = "request_timeout"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    DEPENDENCY_FAILED = "dependency_failed"
    UNKNOWN_ERROR = "unknown_error"
    NETWORK_ERROR = "network_error"
    INVALID_REQUEST = "invalid_request"
    AUDIO_TOO_LARGE = "audio_too_large"
    REQUEST_CANCELLED = "request_cancelled"
    RESOURCE_NOT_FOUND = "resource_not_found"


GROQ_ERROR_MAP = {
    AuthenticationError: GroqFailureReason.AUTHENTICATION_FAILED,
    BadRequestError: GroqFailureReason.INVALID_REQUEST,
    RateLimitError: GroqFailureReason.RATE_LIMITED,
    APITimeoutError: GroqFailureReason.REQUEST_TIMEOUT,
    InternalServerError: GroqFailureReason.PROVIDER_UNAVAILABLE,
    PermissionDeniedError: GroqFailureReason.AUTHENTICATION_FAILED,
    UnprocessableEntityError: GroqFailureReason.INVALID_REQUEST,
    APIConnectionError: GroqFailureReason.NETWORK_ERROR,

}


def translate_groq_error(error):
    """

    :param error:
    :return:
    """
    if isinstance(error, APIStatusError):
        if error.status_code in (500, 502, 503):
            return GroqFailureReason.PROVIDER_UNAVAILABLE
        elif error.status_code == 498:
            return GroqFailureReason.RATE_LIMITED
        elif error.status_code == 413:
            return GroqFailureReason.AUDIO_TOO_LARGE
    for exception_type, failure_reason in GROQ_ERROR_MAP.items():
        if isinstance(error, exception_type):
            return failure_reason
    return GroqFailureReason.UNKNOWN_ERROR


# Whatsapp Automation Failures
class WhatsappFailureReason(Enum):
    CHAT_NOT_FOUND = "chat_not_found"
    MULTIPLE_CHATS_FOUND = "multiple_chats_found"
    ELEMENT_NOT_FOUND = "element_not_found"
    NO_MESSAGES_FOUND = "no_messages_found"
    MISSING_MESSAGE_CONTENT = "missing_message_content"
    UNKNOWN_ERROR = "unknown_error"
    WHATSAPP_UNAVAILABLE = "whatsapp_unavailable"
    ACTION_FAILED = "action_failed"
