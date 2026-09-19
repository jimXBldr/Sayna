from sayna_mvp_v1.contracts.content import ProcessedResult
from sayna_mvp_v1.support.exceptions import InvalidProcessResult


class ContentProcessor:
    def __init__(self, llm_client, content_prompt):
        self._llm_client = llm_client
        self._content_prompt = content_prompt

    def extract_info(self, content: str, query: str) -> ProcessedResult:
        prompt = self._content_prompt.build_extract_info_prompt(content, query)
        content = self._llm_client.generate(prompt=prompt)
        return self._build_processed_result(content)
    def summarize_chat(self, content: str) -> ProcessedResult:
        prompt = self._content_prompt.build_summarization_prompt(content)
        content = self._llm_client.generate(prompt)
        return self._build_processed_result(content)
    def _validate_response(self, llm_response):
        if not isinstance(llm_response.content, str):
            raise InvalidProcessResult('Response must be a string')
        return llm_response

    def _build_processed_result(self, llm_response) -> ProcessedResult:
        if llm_response.success:
            valid_content = self._validate_response(llm_response)
            return ProcessedResult(success=True, processed_result=valid_content.content, failure_reason=None)
        return ProcessedResult(success=False, processed_result=None, failure_reason=llm_response.failure_reason)
