# support/exception.py

class ConfigurationError(Exception):
    """describes the error faced by config.py"""
    pass

class InvalidIntentResponse(Exception):
    pass


class InvalidProcessResult(Exception):
    pass