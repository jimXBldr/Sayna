from playwright.sync_api import sync_playwright
import re
import time

def find_chat(chat: str):
    """
    Find the WhatsApp chat/contact requested by the user and return enough information for the
    Action Manager to proceed or clarify.
    """
    search_box = page.get_by_role("textbox", name="Search or start a new chat")
    search_box.clear()
    search_box.fill(chat)
    results = page.get_by_role('grid', name="Search results.")
    results.wait_for()
    search_results = []
    for i in range(results.count()):
        search_results.append(results.nth(i).inner_text())
    return search_results






if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            headless=False
        )

        page = browser.new_page()
        page.goto("https://web.whatsapp.com")

        input("Log into WhatsApp and press Enter here...")

        print(find_chat('mum'))
        page.pause()
