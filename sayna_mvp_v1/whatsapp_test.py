# Make use of the locators here
"""
run_whatsapp_test.py

Focused verification script.

CHANGELOG (round 4 -- per live-run feedback):
  - Search now goes through the New Chat panel (search_contacts_panel /
    open_chat_via_new_chat), NOT the main pane's search box. The main
    pane's search sits directly on top of your already-rendered recent-
    chats list, so for any contact you already have an open chat with,
    its row is visible before you've typed anything -- a plain
    "does a matching row exist" wait passes instantly, before WhatsApp
    has actually finished filtering the rest of the list out. That's
    confirmed by the last run: '.april' (no existing chat) filtered down
    to 4 results correctly; 'Mubby' and 'Subomi' (existing chats) came
    back with the full ~66-chat list, unfiltered, every time. The New
    Chat panel is a dedicated contacts search with no such overlay
    confound.
  - is_from_me was silently False for every single message in the last
    run, including ones that were clearly the account owner's own text
    (matching a prior test-message signature). Fixed in
    whatsapp_action_manager.py's _parse_message -- see its docstring.
  - send_message() now verifies the composer actually cleared after the
    send attempt and raises if it didn't, rather than returning
    successfully on what may have been a silent no-op (the prior run's
    "sent" messages never actually showed up on reread at all).
  - test_send_and_verify polls for up to 4s (5 attempts) for the new
    message to appear, instead of one fixed 800ms sleep + a single read.
"""

from __future__ import annotations

import os
import sys
import uuid
from dataclasses import dataclass

from playwright.sync_api import sync_playwright

from whatsapp_action_manager import WhatsAppActionManager, LocatorNotFoundError, ActionBlockedError

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class Config:
    chrome_executable_path: str
    headless: bool


def load_config() -> Config:
    path = os.environ.get("CHROME_EXECUTABLE_PATH")
    if not path:
        print("ERROR: CHROME_EXECUTABLE_PATH environment variable is not set.")
        sys.exit(1)
    headless_raw = os.environ.get("HEADLESS", "false").strip().lower()
    return Config(chrome_executable_path=path, headless=headless_raw == "true")


TEST_CONTACTS = ["Mubby", "april", "Subomi"]
MIN_MESSAGES_TO_READ = 20


def test_search_via_new_chat(manager: WhatsAppActionManager, query: str) -> tuple[bool, bool]:
    """
    Opens the New Chat panel, records its baseline result count BEFORE
    typing, types `query` into the panel's own search box, waits for the
    result set to actually settle (not just "a matching row exists" --
    see wait_for_results_settled's docstring), then checks:
      - matched: at least one visible title contains `query`
      - filtered: the post-type count is smaller than the baseline
    Leaves the New Chat panel OPEN on return (caller opens the chat next).
    """
    manager.open_new_chat_panel()
    baseline = manager.get_search_results()
    baseline_titles = [r["title"] for r in baseline if r["title"]]

    manager.search_contacts_panel(query)
    manager.wait_for_results_settled()

    results = manager.get_search_results()
    titles = [r["title"] for r in results if r["title"]]

    matched = any(query.lower() in t.lower() for t in titles)
    filtered = len(titles) < len(baseline_titles)

    print(f"  [search test] query='{query}': {len(titles)} visible result(s) in New Chat panel "
          f"(baseline before typing: {len(baseline_titles)})")
    for r in results[:15]:
        print(f"    [{r['index']}] {r['title']}")
    if len(results) > 15:
        print(f"    ... +{len(results) - 15} more")

    if matched and filtered:
        print(f"  [search test] PASS -- '{query}' matched and the New Chat panel list was filtered")
    elif matched and not filtered:
        print(f"  [search test] SUSPECT -- '{query}' matched but the count didn't shrink "
              f"({len(titles)} vs baseline {len(baseline_titles)})")
    else:
        print(f"  [search test] FAIL -- no visible row contained '{query}'")

    return matched, filtered


def test_send_and_verify(manager: WhatsAppActionManager, active_title: str) -> bool:
    """
    Sends a UUID-tagged message, then polls (up to ~4s) for it to appear
    in the reread message list with is_from_me=True.
    """
    tag = uuid.uuid4().hex[:8]
    text = f"Playwright send-test {tag}"

    try:
        manager.send_message(text)
    except ActionBlockedError as e:
        print(f"  [send test] FAIL -- send_message detected the composer never cleared: {e}")
        return False
    except Exception as e:  # noqa: BLE001
        print(f"  [send test] FAIL -- send_message raised: {e}")
        return False

    for attempt in range(5):
        manager.page.wait_for_timeout(800)
        messages = manager.get_recent_messages(min_n=5, hard_cap=20)
        landed = any(m.content == text and m.is_from_me for m in messages)
        if landed:
            print(f"  [send test] PASS -- '{text}' confirmed in {active_title}'s message list, "
                  f"is_from_me=True (seen after {attempt + 1} check(s))")
            return True

    print(f"  [send test] FAIL -- '{text}' not found as is_from_me=True after 5 checks (~4s). "
          f"Last few messages read back:")
    for m in messages[-5:]:
        print(f"    is_from_me={m.is_from_me} sender={m.sender!r} content={m.content!r}")
    return False


def run_contact_flow(manager: WhatsAppActionManager, name: str) -> dict:
    print(f"\n{'=' * 60}\nContact: {name}\n{'=' * 60}")
    result = {"contact": name, "search_ok": False, "opened": False, "read_ok": False, "send_ok": False}

    matched, filtered = test_search_via_new_chat(manager, name)
    result["search_ok"] = matched and filtered

    opened = manager.open_result_by_name(name)
    if not opened:
        print(f"  Could not open a chat for '{name}' from the New Chat panel results.")
        manager.close_new_chat_panel()
        return result
    result["opened"] = True

    active_title = manager.get_active_chat_title()
    print(f"  Opened chat. Active chat title: '{active_title}'")

    try:
        messages = manager.get_recent_messages(min_n=MIN_MESSAGES_TO_READ, hard_cap=200)
        print(f"  Read {len(messages)} message(s). Most recent: "
              f"{messages[-1].content[:60] if messages else '(none)'}")
        result["read_ok"] = True
    except Exception as e:  # noqa: BLE001
        print(f"  [read test] FAIL -- {e}")

    result["send_ok"] = test_send_and_verify(manager, active_title)

    return result


def main() -> None:
    config = load_config()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=config.chrome_executable_path,
            headless=config.headless,
        )
        page = browser.new_page()
        page.goto("https://web.whatsapp.com")

        input("Log into WhatsApp then press Enter...")

        manager = WhatsAppActionManager(page, debug_dir=os.path.dirname(os.path.abspath(__file__)) or ".")

        report = manager.verify_locators()
        manager.print_locator_report(report)

        pull_contacts = input("Pull the full contacts list too? Already confirmed working "
                               "and can take a while on a large account (y/N): ").strip().lower()
        if pull_contacts == "y":
            try:
                contacts = manager.get_all_contacts()
                print(f"\nAll contacts ({len(contacts)}) -- showing first 20:")
                for name in contacts[:20]:
                    print(f"  - {name}")
                if len(contacts) > 20:
                    print(f"  ... +{len(contacts) - 20} more")
            except (ActionBlockedError, LocatorNotFoundError) as e:
                print(f"  Contacts pull failed: {e}")

        results = [run_contact_flow(manager, contact) for contact in TEST_CONTACTS]

        print(f"\n{'=' * 60}\nSummary\n{'=' * 60}")
        for r in results:
            print(f"  {r['contact']:<10} search={'OK' if r['search_ok'] else 'FAIL':<5} "
                  f"opened={'OK' if r['opened'] else 'FAIL':<5} "
                  f"read={'OK' if r['read_ok'] else 'FAIL':<5} "
                  f"send={'OK' if r['send_ok'] else 'FAIL':<5}")

        input("\nDone. Press Enter to close the browser...")
        browser.close()


if __name__ == "__main__":
    main()