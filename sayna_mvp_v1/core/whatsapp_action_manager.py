from sayna_mvp_v1.contracts.action import ActionResult
from sayna_mvp_v1.support.errors_translator import WhatsappFailureReason

class WhatsappActionManager:
    def __init__(self, automation):
        self._automation = automation

    def open_chat(self, chat) -> ActionResult:
        result = self._automation.find_chat(chat)
        if result.success:
            self._automation.click_chat(result.locator)
            return ActionResult(success=True, data=None, failure_reason=None, matches=result.matches)
        return ActionResult(success=False, data=None, failure_reason=result.failure_reason, matches=result.matches)

    def send_message(self, chat: str, message: str) -> ActionResult:
        action_result = self.open_chat(chat)
        if action_result.success:
            self._automation.type_message(message)
            self._automation.click_send()
            return ActionResult(success=True, data=None, failure_reason=None, matches=None)
        return ActionResult(success=False, data=None, failure_reason=action_result.failure_reason, matches=None)

    def get_content(self, chat) -> ActionResult:
        messages = self._automation.get_messages(chat)
        if messages.success:
            return ActionResult(success=True, data=messages.content, failure_reason=None, matches=None)
        return ActionResult(success=False, data=None, failure_reason=messages.failure_reason, matches=None)