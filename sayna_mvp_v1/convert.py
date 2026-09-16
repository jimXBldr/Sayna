from playwright.sync_api import sync_playwright
from sayna_mvp_v1.contracts.action import ChatMatchResult, MessageResult
from sayna_mvp_v1.support.errors_translator import WhatsappFailureReason
import re


def get_messages(chat):
    chat = find_chat(chat)
    if chat.success:
        chat.locator.click()
        messages = page.get_by_test_id(re.compile("^conv-msg-"))
        contents = []
        for i in range(messages.count()):
            contents.append(messages.nth(i).inner_text())
        return MessageResult(success=True, content=contents, failure_reason=None)
    return MessageResult(success=False, content=None,failure_reason=None)


def find_chat(chat: str):
    """
    Find the WhatsApp chat/contact requested by the user and return enough information for the
    Action Manager to proceed or clarify.
    """
    search_box = page.get_by_role("textbox", name="Search or start a new chat")
    search_box.clear()
    search_box.fill(chat)
    page.wait_for_timeout(2000)
    results = page.get_by_role(role='grid', name='Search results.')
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


if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            headless=False
        )

        page = browser.new_page()
        page.goto("https://web.whatsapp.com")

        input("Log into WhatsApp and press Enter here...")

        messages = get_messages('Subomi Obans')
        print(messages)
        message_box = page.get_by_role('paragraph')
        print('Gotten the messaging editable component')
        message_box.fill('Are you in class?')
        print('Message typed')
        page.get_by_test_id("compose-box").get_by_role("button", name="Send").click()
        print('Sent')

        page.pause()