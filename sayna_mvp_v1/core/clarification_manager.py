from sayna_mvp_v1.contracts.clarification import ClarificationResult, ClarificationRequest
from sayna_mvp_v1.support.errors_translator import WhatsappFailureReason


class ClarificationManager:
    def __init__(self, llm_client, clarification_prompt):
        self._llm_client = llm_client
        self._clarification_prompt = clarification_prompt

    def generate_question(self, clarification_request: ClarificationRequest):
        if clarification_request.failure_reason == WhatsappFailureReason.MULTIPLE_CHATS_FOUND:
            question = f'Which of these contacts are you referring to ? \n {clarification_request.parameters}'
            return question
        elif clarification_request.failure_reason == 'missing intent field':
            question = f''

    def interpret_response(self, clarification_request: ClarificationRequest):
        if clarification_request.new_parameter:
            update_parameter = self._clarification_prompt.extract_parameter(clarification_request.new_parameter)
            return ClarificationResult(success=True, updated_parameters=update_parameter, failure_reason=None)
