import re

from sayna_mvp_v1.contracts.action import ChatMatchResult, MessageResult
from sayna_mvp_v1.support.errors_translator import WhatsappFailureReason


class WhatsappAutomationManager:
    def __init__(self, page):
        self._page = page

    def find_chat(self, chat: str) -> ChatMatchResult:
        search_box = self._page.get_by_role("textbox").first
        search_box.fill(chat)
        self._page.wait_for_timeout(2000)
        results = self._page.get_by_role(role='grid', name='Search results.')
        contact = results.get_by_test_id('cell-frame-container')
        contacts = []
        for i in range(contact.count()):
            title = contact.nth(i).get_by_test_id("cell-frame-title")
            if title.count() > 0 and title.is_visible():
                contacts.append(title.inner_text())
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

    def get_messages(self, chat: str):
        chat_name = chat
        chat = self.find_chat(chat)
        if chat.success:

            self.click_chat(chat.locator)
            messages = self._page.get_by_test_id(re.compile("^conv-msg-"))
            contents = []
            for i in range(messages.count()):
                message = messages.nth(i)
                if message.get_by_test_id("tail-in").count() > 0:
                    sender = chat_name
                elif message.get_by_test_id('tail-out').count() > 0:
                    sender = "Me"
                contents.append(f"{sender}: {messages.nth(i).inner_text()}")
            if len(contents) == 0:
                return MessageResult(success=False, content=None,
                                     failure_reason=WhatsappFailureReason.NO_MESSAGES_FOUND, matches=None)
            return MessageResult(success=True, content=contents, failure_reason=None, matches=chat.matches)
        return MessageResult(success=False, content=None, failure_reason=chat.failure_reason,
                             matches=chat.matches)

    def click_send(self):
        self._page.get_by_test_id("compose-box").get_by_role("button", name="Send").click()

    def type_message(self, message):
        message_box = self._page.get_by_role('paragraph')
        message_box.clear()
        message_box.fill(message)

    def get_contacts(self) -> list[str]:
        pass


class BrowserAutomationManager:
    """
"""
