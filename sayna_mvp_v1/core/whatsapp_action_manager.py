class WhatsappActionManager:
    def __init__(self, automation):
        self._automation = automation
        pass

    def open_chat(self, chat: str):
        """
        Receive chat name

            ↓

        Locate chat(s)

            ↓

        No chats

        → failure

            ↓

        One chat

            ↓

        Open chat

            ↓

        Success

            ↓

        Multiple chats

            ↓

        Failure
        """
        pass

    def get_content(self, chat: str):
        """
        Receive chat

            ↓

        open_chat(chat)

            ↓

        Scroll if necessary

            ↓

        Extract last N messages

            ↓

        Return messages
        """
        pass

    def send_message(self, chat, message: str):
        """
        Receive chat and message

            ↓

        open_chat(chat)

            ↓

        Type message

            ↓

        Click send

            ↓
        Success
        """
        pass

    def _chat_locator(self, chat):
        """
        Receive chat name

        Ensure WhatsApp is available

        Clear the search box

        Type the chat name into the search box

        Wait for search results

        Count matching chats

        If no chats are found
            return CHAT_NOT_FOUND

        If exactly one chat is found
            return Locator to that chat

        If multiple exact matches are found
            Extract every displayed chat title
            return MULTIPLE_CHATS_FOUND with list of names

        If multiple chats are found but no exact matches

        """
        pass