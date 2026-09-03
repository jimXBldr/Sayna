"""
Provide a browser-automation interface for interacting with WhatsApp Web without exposing
Playwright-specific implementation details to the rest of Sayna.
"""
from sayna_mvp_v1.contracts.action import ChatMatchResult
from sayna_mvp_v1.support.errors_translator import WhatsappFailureReason
import re

class WhatsappAutomationManager:
    def __init__(self, page):
        self._page = page
        pass

    def find_chat(self, chat: str) -> ChatMatchResult:
        """
        Find the WhatsApp chat/contact requested by the user and return enough information for the
        Action Manager to proceed or clarify.
        """
        search_box = self._page.get_by_role("textbox", name="Search or start a new chat")
        search_box.clear()
        search_box.fill(chat)
        results = self._page.get_by_test_id(re.compile("^list-item-"))
        search_results = []
        for i in range(results.count):
            search_results.append(results.nth(i).inner_text())
        return search_results



    def click_chat(self, locator):
        pass

    def get_messages(self):
        pass

    def click_send(self):
        pass
