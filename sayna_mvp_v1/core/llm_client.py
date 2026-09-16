# core/llm_client.py
from sayna_mvp_v1.support.errors_translator import translate_groq_error
from sayna_mvp_v1.contracts.llm import LLMResult


class LLMClient:
    def __init__(self, groq_client, model):
        self._groq_client = groq_client
        self._model = model

    def generate(self, prompt: str) -> LLMResult:
        try:
            response = self._groq_client.chat.completions.create(
                messages=prompt, model=self._model
            )
            content = self._extract_content_response(response)
            return LLMResult(success=True, content=content, failure_reason=None)
        except Exception as e:
            failure_reason = translate_groq_error(e)
            return LLMResult(success=False, content=None, failure_reason=failure_reason)

    def _extract_content_response(self, response):
        return response.choices[0].message.content
