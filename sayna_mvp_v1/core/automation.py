"""
Provide a browser-automation interface for interacting with WhatsApp Web without exposing
Playwright-specific implementation details to the rest of Sayna.
"""
import re

from sayna_mvp_v1.contracts.action import ChatMatchResult, MessageResult
from sayna_mvp_v1.support.errors_translator import WhatsappFailureReason


class WhatsappAutomationManager:
    def __init__(self, page):
        self._page = page

    def find_chat(self, chat: str) -> ChatMatchResult:
        """
        Find the WhatsApp chat/contact requested by the user and return enough information for the
        Action Manager to proceed or clarify.
        """
        search_box = self._page.get_by_role("textbox", name="Search or start a new chat")
        search_box.clear()
        search_box.fill(chat)
        self._page.wait_for_timeout(3000)
        results = self._page.get_by_role(role='grid', name='Search results.')
        contact = results.get_by_test_id('cell-frame-container')
        contacts = []
        for i in range(contact.count()):
            contacts.append(contact.nth(i).get_by_test_id('cell-frame-title').inner_text())
        for index, i in enumerate(contacts):
            if '\n' in i:
                contacts[index] = i.split('\n')[-1]
        exact_matches = []
        for i, candidates_name in enumerate(contacts):
            if candidates_name.strip().lower() == chat.strip().lower():
                exact_matches.append(candidates_name)
                locator_index = i
        if len(contacts) == 0:
            return ChatMatchResult(success=False, locator=None, matches=None,
                                   failure_reason=WhatsappFailureReason.CHAT_NOT_FOUND)
        elif len(contacts) == 1:
            return ChatMatchResult(success=True, locator=contact.nth(0).get_by_test_id('cell-frame-title'),
                                   matches=None, failure_reason=None)
        elif len(exact_matches) == 0:
            return ChatMatchResult(success=False, locator=None, matches=contacts,
                                   failure_reason=WhatsappFailureReason.MULTIPLE_CHATS_FOUND)
        elif len(exact_matches) > 1:
            return ChatMatchResult(success=False, locator=None, matches=exact_matches,
                                   failure_reason=WhatsappFailureReason.MULTIPLE_EXACT_CHATS_FOUND)
        elif len(exact_matches) == 1:
            return ChatMatchResult(success=True, locator=contact.nth(locator_index).get_by_test_id('cell-frame-title'),
                                   matches=None, failure_reason=None)
        else:
            return ChatMatchResult(success=False, locator=None, matches=None,
                                   failure_reason=WhatsappFailureReason.UNKNOWN_ERROR)

    def click_chat(self, locator):
        locator.click()

    def get_messages(self, chat):
        chat = self.find_chat(chat)
        if chat.success:
            self.click_chat(chat.locator)
            messages = self._page.get_by_test_id(re.compile("^conv-msg-"))
            contents = []
            for i in range(messages.count()):
                contents.append(messages.nth(i).inner_text())
            return MessageResult(success=True, content=contents, failure_reason=None)
        return MessageResult(success=False, content=None, failure_reason=WhatsappFailureReason.UNKNOWN_ERROR)

    def click_send(self):
        pass



    def type_message(self, message):
        self._page
        pass

    def get_contacts(self) -> list[str]:
        pass