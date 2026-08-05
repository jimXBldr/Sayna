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
        if "intent" not in response or "parameters" not in response:
            raise InvalidIntentResponse('Fields are missing')
        if not isinstance(response['intent'], str):
            raise InvalidIntentResponse('intent is not a string')
        if not isinstance(response['parameters'], dict):
            raise InvalidIntentResponse('Parameter isnt a dictionary')
        if response['intent'].strip() == "":
            raise InvalidIntentResponse('Intent is empty')
        for key in response["parameters"]:
            if not isinstance(key, str):
                raise InvalidIntentResponse('parameters isnt a string')

        return response

    def _build_intent_result(self, response: LLMResult) -> IntentResult:
        try:
            parse_response = json.loads(response.content)
        except json.JSONDecodeError:
            raise InvalidIntentResponse('LLM returned invalid json')
        parsed_response = self._validate_response(parse_response)
        structured_request = StructuredRequest(intent=parsed_response['intent'], parameters=parsed_response['parameters'])
        return IntentResult(success=True, structured_request=structured_request, failure_reason=None)
