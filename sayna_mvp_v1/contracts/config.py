# contracts/config.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    groq_api_key: str
    stt_model: str
    stt_response_format: str
    llm_model: str
    language: str

