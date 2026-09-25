import re

from sayna_mvp_v1.contracts.action import ChatMatchResult, MessageResult
from sayna_mvp_v1.support.errors_translator import WhatsappFailureReason


class WhatsappAutomationManager:
    def __init__(self, page):
        self._page = page

    def find_chat(self, chat: str) -> ChatMatchResult:
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
            if len(contents) == 0:
                return MessageResult(success=False, content=None, failure_reason=WhatsappFailureReason.NO_MESSAGES_FOUND)
            return MessageResult(success=True, content=contents, failure_reason=None)
        return MessageResult(success=False, content=None, failure_reason=WhatsappFailureReason.UNKNOWN_ERROR)

    def click_send(self):
        self._page.get_by_test_id("compose-box").get_by_role("button", name="Send").click()

    def type_message(self, message):
        message_box = self._page.get_by_role('paragraph')
        message_box.clear()
        message_box.fill(message)

    def get_contacts(self) -> list[str]:
        pass

class BrowserAutomationManager:
    """Its not a bug its just the way I set it but now I have changed it in the code base sha



if len(contents) == 0:
    return MessageResult(success=False, content=None, failure_reason=WhatsappFailureReason.NO_MESSAGES_FOUND)





But the bigger promblem is that conv-msg doesnt specify who sent the message like it just the list of the messages like the messages in order doesnt specify who sent it for instance  here is the first message I Sent 'Please help me to sign attendance\n12:59 PM', the second message was the one SUbomi sent 'Whats your reason for not coming to class?\n1:04 PM'



C:\Users\hp\PycharmProjects\learning_logR\.venv\Scripts\python.exe "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\convert.py"

Log into WhatsApp and press Enter here...

MessageResult(success=True, content=['No\n8:06 AM', 'We had that yesterday\n8:07 AM', 'Subomi Obans\nWe had that yesterday\nAlright\n8:11 AM', 'Please help me to sign attendance\n12:59 PM', 'Whats your reason for not coming to class?\n1:04 PM', "Subomi Obans\nWhats your reason for not coming to class?\nWas in severe pain through out the night couldn't sleep\n1:33 PM", "Yo what's up?\n4:51 PM", "Subomi Obans\nYo what's up?\nAre you going for the match?\n4:54 PM", 'Which match?\n4:55 PM', 'Subomi Obans\nWhich match?\nDw I thought today is the match between Cossa exec and freshers\n4:58 PM'], failure_reason=None)

Here is the extracted content: ProcessedResult(success=True, processed_result='Subomi said the match today is the one between the Cossa exec and the freshers, and he asked if you were going to attend it.', failure_reason=None)

Here is the summarized content: ProcessedResult(success=True, processed_result='The conversation starts with a brief exchange about an event that was “had yesterday.” Later, a request is made to sign attendance, followed by a question about the reason for missing class. The response explains the absence was due to severe pain that prevented sleep. In the evening, the chat turns casual with a “Yo what’s up?” message. The speaker asks if the other person is going to a match, and after a brief clarification about which match, it’s revealed that today’s match is between the Cossa executive team and the freshers.', failure_reason=None)





C:\Users\hp\PycharmProjects\learning_logR\.venv\Scripts\python.exe "C:\Users\hp\Desktop\super folder\Libary\SAYNA\sayna_mvp_v1\convert.py"

Log into WhatsApp and press Enter here...

MessageResult(success=True, content=['Please help me to sign attendance\n12:59 PM', 'Whats your reason for not coming to class?\n1:04 PM', "Subomi Obans\nWhats your reason for not coming to class?\nWas in severe pain through out the night couldn't sleep\n1:33 PM", "Yo what's up?\n4:51 PM", "Subomi Obans\nYo what's up?\nAre you going for the match?\n4:54 PM", 'Which match?\n4:55 PM', 'Subomi Obans\nWhich match?\nDw I thought today is the match between Cossa exec and freshers\n4:58 PM', 'Hello boy how are you doing\n9:25 PM', 'I am just checking something dont mind me\n9:26 PM', '3\n9:30 PM'], failure_reason=None)

Here is the extracted content: ProcessedResult(success=True, processed_result='Subomi said that the match on that day was the one between the Cossa executive team and the freshers.', failure_reason=None)

Here is the summarized content: ProcessedResult(success=True, processed_result='The conversation began with a request to help sign attendance. A follow‑up message asked why the user missed class, to which they replied that they were in severe pain all night and could not sleep. Later that afternoon, the two exchanged casual “yo” greetings and a brief chat about a match, with the user clarifying it was the Cossa executive versus fresher game happening that day. In the late evening, a short hello was sent, followed by a quick check‑in, and the last message simply read “3.”', failure_reason=None)


"""