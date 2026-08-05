# support/config.py
"""
Provides a centralized validated resources needed to bootstrap the application
"""
import os
from sayna_mvp_v1.support.exceptions import ConfigurationError
from dotenv import load_dotenv
from sayna_mvp_v1.contracts.config import Config

load_dotenv()


def load_config() -> Config:
    configurations = {
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "stt_model": os.getenv("STT_MODEL"),
        "stt_response_format": os.getenv("STT_RESPONSE_FORMAT"),
        "llm_model": os.getenv("LLM_MODEL")
    }
    missing_values = []
    for key, value in configurations.items():
        if value is None or value.strip() == "":
            missing_values.append(key)
    if missing_values:
        raise ConfigurationError(f"Missing Required configuration:{','.join(missing_values)}")
    return Config(**configurations)
