"""
get_contacts_only.py

Minimal script: log in, pull the full WhatsApp contacts list (via the
"New chat" panel -- this is your whole address book, not just chats you
already have open), print it, exit. No message reading/sending, no
locator report noise.

Env vars:
    CHROME_EXECUTABLE_PATH   (required)
    HEADLESS                 (optional, "true"/"false", default "false")
"""

from __future__ import annotations

import os
import sys

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

from whatsapp_action_manager import WhatsAppActionManager

load_dotenv()


def main() -> None:
    chrome_path = os.environ.get("CHROME_EXECUTABLE_PATH")
    if not chrome_path:
        print("ERROR: CHROME_EXECUTABLE_PATH environment variable is not set.")
        sys.exit(1)
    headless = os.environ.get("HEADLESS", "false").strip().lower() == "true"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=chrome_path, headless=headless)
        page = browser.new_page()
        page.goto("https://web.whatsapp.com")

        input("Log into WhatsApp then press Enter...")

        manager = WhatsAppActionManager(page, debug_dir=os.path.dirname(os.path.abspath(__file__)) or ".")
        contacts = manager.get_all_contacts()

        print(f"\nAll contacts ({len(contacts)}):")
        for name in contacts:
            print(f"  - {name}")

        browser.close()


if __name__ == "__main__":
    main()