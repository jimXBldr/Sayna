from playwright.sync_api import sync_playwright

CHAT_QUERY = "Daddy"
MESSAGE = "Hello from Playwright!"


def verify(name: str, condition: bool):
    if not condition:
        raise Exception(f"[FAIL] {name}")
    print(f"[PASS] {name}")


with sync_playwright() as p:

    browser = p.chromium.launch(
        executable_path=r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        headless=False,
    )

    page = browser.new_page()

    page.goto("https://web.whatsapp.com")

    input("Log into WhatsApp then press Enter...")

    # ---------------------------------------------------------
    # SEARCH BOX
    # ---------------------------------------------------------

    search_box = page.get_by_role(
        "textbox",
        name="Search or start a new chat"
    )

    verify(
        "Search box located",
        search_box.count() == 1
    )

    search_box.click()
    search_box.fill(CHAT_QUERY)

    page.wait_for_timeout(1500)

    print("\nSearching for:", CHAT_QUERY)

    # ---------------------------------------------------------
    # COLLECT MATCHING CHATS
    # ---------------------------------------------------------

    matches = []

    index = 1

    while True:

        item = page.get_by_test_id(f"list-item-{index}")

        if item.count() == 0:
            break

        title_locator = item.get_by_test_id("cell-frame-title")

        if title_locator.count() == 0:
            index += 1
            continue

        try:
            title = title_locator.inner_text().strip()

            if title:
                matches.append(
                    {
                        "index": index,
                        "title": title,
                        "locator": item,
                    }
                )

        except Exception:
            pass

        index += 1

    print("\n==============================")

    if not matches:
        print("No matching chats found.")
        browser.close()
        raise SystemExit()

    print(f"Found {len(matches)} matching chat(s):\n")

    for match in matches:
        print(
            f"{match['index']}. {match['title']}"
        )

    print("\n==============================")

    verify(
        "Collected search results",
        len(matches) > 0
    )

    # ---------------------------------------------------------
    # OPEN FIRST RESULT (verification only)
    # ---------------------------------------------------------

    matches[0]["locator"].click()

    print(
        f"\nOpened: {matches[0]['title']}"
    )

    page.wait_for_timeout(1000)

    # ---------------------------------------------------------
    # MESSAGE INPUT
    # ---------------------------------------------------------

    message_box = page.get_by_test_id(
        "conversation-compose-box-input"
    )

    verify(
        "Message input located",
        message_box.count() == 1
    )

    message_box.click()

    page.keyboard.type(MESSAGE)

    print("[PASS] Typed message")

    page.wait_for_timeout(500)

    # ---------------------------------------------------------
    # SEND BUTTON
    # ---------------------------------------------------------

    send_button = page.get_by_role(
        "button",
        name="Send"
    )

    verify(
        "Send button located",
        send_button.count() == 1
    )

    answer = input(
        "\nSend the message? (y/n): "
    )

    if answer.lower() == "y":
        send_button.click()
        print("[PASS] Message sent.")
    else:
        print("[SKIPPED] Message not sent.")

    page.pause()