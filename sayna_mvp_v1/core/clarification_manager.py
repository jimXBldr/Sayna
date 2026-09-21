from sayna_mvp_v1.contracts.clarification import ClarificationResult
class ClarificationManager:
    def __init__(self, llm_client,  clarification_prompt):
        self._llm_client = llm_client
        self._clarification_prompt = clarification_prompt

    def generate_question(self, parameters) -> ClarificationResult:
        prompt_question = self._clarification_prompt.build(parameters)
        llm_response = self._llm_client.generate(prompt_question)
        return ClarificationResult()


    def interpret_response(self):
        pass
