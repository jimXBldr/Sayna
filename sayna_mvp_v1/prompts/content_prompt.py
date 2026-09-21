class ContentProcessorPrompt:
    EXTRACT_INFO_PROMPT = """
    You are the content processor for a voice controlled whatsapp application.
    
    Find the information requested by the query within the supplied WhatsApp content and 
    formulate the result for the user.
    
    Don't use outside knowledge to answer the query. Only use information present in the supplied WhatsApp content.
    
    Do not explain your reasoning.
    
    Rules:
    If the requested query can not be extracted from the given whatsapp content return that the the requested 
    information cant be gotten from content message. """

    SUMMARIZE_CHAT_PROMPT = """
     You are the content processor for a voice controlled whatsapp application.
     Your job is to return a summary given a contents of whatsapp chats.
    """

    def build_extract_info_prompt(self, content, query) -> list[dict[str, str]]:
        prompt = [
            {
                "role": "system",
                "content": self.EXTRACT_INFO_PROMPT
            },

            {
                "role": "user",
                "content": f"Content: \n {content}, Query to be extracted: \n {query}"
            }
        ]
        return prompt

    def build_summarization_prompt(self, content) -> list[dict[str, str]]:
        prompt = [
            {
                "role": "system",
                "content": self.SUMMARIZE_CHAT_PROMPT
            },

            {
                "role": "user",
                "content": f"Content: \n {content}"
            }
        ]
        return prompt
