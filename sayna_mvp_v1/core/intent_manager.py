# CORE/ intent_manager.py
import json
from sayna_mvp_v1.support.exceptions import InvalidIntentResponse
from sayna_mvp_v1.contracts.llm import LLMResult
from sayna_mvp_v1.contracts.intent import IntentResult, StructuredRequest


class IntentManager:
    def __init__(self, llm_client, intent_prompt):
        self._llm_client = llm_client
        self._intent_prompt = intent_prompt

    def detect_intent(self, transcript: str) -> IntentResult:
        prompt = self._intent_prompt.build_intent_prompt(transcript)
        llm_response = self._llm_client.generate(prompt=prompt)
        if not llm_response.success:
            return IntentResult(success=False, structured_request=None, failure_reason=llm_response.failure_reason)
        return self._build_intent_result(llm_response)

    def _validate_response(self, response: dict) -> dict:
        if not isinstance(response, dict):
            raise InvalidIntentResponse('LLM response must be a JSON object.')
        if "intent" not in response:
            raise InvalidIntentResponse('Missing Intent Field.')
        if "parameters" not in response:
            raise InvalidIntentResponse('Missing Parameter Field.')
        if not isinstance(response['intent'], str) and not response['intent'] is None:
            raise InvalidIntentResponse('Intent must be a string and None')
        if not isinstance(response['parameters'], dict):
            raise InvalidIntentResponse('Parameter must be a dictionary')

        return response

    def _build_intent_result(self, response: LLMResult) -> IntentResult:
        try:
            parse_response = json.loads(response.content)
            valid_response = self._validate_response(parse_response)
            structured_request = StructuredRequest(intent=valid_response['intent'],
                                                   parameters=valid_response['parameters'])
            return IntentResult(success=True, structured_request=structured_request, failure_reason=None)
        except (InvalidIntentResponse, json.JSONDecodeError) as e:
            return IntentResult(success=False, structured_request=None, failure_reason=e)

