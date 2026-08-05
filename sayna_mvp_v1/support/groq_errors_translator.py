# support/groq_errors_translators.py

from enum import Enum
from groq import (AuthenticationError, BadRequestError,
                  RateLimitError, APITimeoutError,
                  InternalServerError, PermissionDeniedError,
                  APIConnectionError, UnprocessableEntityError, APIStatusError)


class FailureReason(Enum):
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


ERROR_MAP = {
    AuthenticationError: FailureReason.AUTHENTICATION_FAILED,
    BadRequestError: FailureReason.INVALID_REQUEST,
    RateLimitError: FailureReason.RATE_LIMITED,
    APITimeoutError: FailureReason.REQUEST_TIMEOUT,
    InternalServerError: FailureReason.PROVIDER_UNAVAILABLE,
    PermissionDeniedError: FailureReason.AUTHENTICATION_FAILED,
    UnprocessableEntityError: FailureReason.INVALID_REQUEST,
    APIConnectionError: FailureReason.NETWORK_ERROR,

}


def translate_error(error):
    """

    :param error:
    :return:
    """
    if isinstance(error, APIStatusError):
        if error.status_code in (500, 502, 503):
            return FailureReason.PROVIDER_UNAVAILABLE
        elif error.status_code == 498:
            return FailureReason.RATE_LIMITED
        elif error.status_code == 413:
            return FailureReason.AUDIO_TOO_LARGE
    for exception_type, failure_reason in ERROR_MAP.items():
        if isinstance(error, exception_type):
            return failure_reason
    return FailureReason.UNKNOWN_ERROR
