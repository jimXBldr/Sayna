from playwright.sync_api import Page

from sayna_mvp_v1.contracts.action import ActionResult
from sayna_mvp_v1.contracts.intent import StructuredRequest


class WhatsAppActionManager:
    def __init__(self, page: Page):
        self._page = page

    def execute(self, structured_request: StructuredRequest) -> ActionResult:
        try:
            match structured_request.intent:

                case "open_chat":
                    self._open_chat(
                        chat_name=structured_request.parameters["chat"]
                    )

                case "send_message":
                    self._send_message(
                        chat_name=structured_request.parameters["chat"],
                        message=structured_request.parameters["message"],
                    )

                case _:
                    raise ValueError(
                        f"Unsupported intent: {structured_request.intent}"
                    )

            return ActionResult(
                success=True,
                data=None,
                failure_reason=None,
            )

        except Exception as e:
            return ActionResult(
                success=False,
                data=None,
                failure_reason=e,
            )

    def _open_chat(self, chat_name: str) -> None:
        search_box = self._page.get_by_role(
            "textbox",
            name="Search or start a new chat",
        )

        if search_box.count() != 1:
            raise RuntimeError(
                "WhatsApp search box not found."
            )

        search_box.click()
        search_box.fill(chat_name)

        self._page.wait_for_timeout(1500)

        chat_result = self._page.get_by_test_id(
            "list-item-1"
        )

        if chat_result.count() == 0:
            raise RuntimeError(
                f"Chat '{chat_name}' not found."
            )

        chat_result.click()

    def _send_message(
        self,
        chat_name: str,
        message: str | None,
    ) -> None:

        if message is None or message.strip() == "":
            raise ValueError(
                "Cannot send message without message content."
            )

        self._open_chat(chat_name)

        message_box = self._page.get_by_test_id(
            "conversation-compose-box-input"
        )

        if message_box.count() != 1:
            raise RuntimeError(
                "Message input not found."
            )

        message_box.click()
        self._page.keyboard.type(message)

        send_button = self._page.get_by_role(
            "button",
            name="Send",
        )

        if send_button.count() != 1:
            raise RuntimeError(
                "Send button not found."
            )

        send_button.click()