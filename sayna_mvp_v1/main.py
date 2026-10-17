from playwright.sync_api import sync_playwright
from sayna_mvp_v1.core.content_processor import ContentProcessor
from sayna_mvp_v1.prompts.content_prompt import ContentProcessorPrompt
from sayna_mvp_v1.core.llm_client import LLMClient
from sayna_mvp_v1.support.config import load_config
from groq import Groq
from sayna_mvp_v1.core.automation import WhatsappAutomationManager
from sayna_mvp_v1.core.whatsapp_action_manager import WhatsappActionManager

configurations = load_config()

groq_client = Groq(api_key=configurations.groq_api_key)

llm_client = LLMClient(model=configurations.llm_model, groq_client=groq_client)

content_prompt = ContentProcessorPrompt()

content_processor = ContentProcessor(llm_client=llm_client, content_prompt=content_prompt)


if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            headless=False
        )

        page = browser.new_page()
        page.goto("https://web.whatsapp.com")

        input("Log into WhatsApp and press Enter here...")
        automation = WhatsappAutomationManager(page)
        whatsapp_action_manger = WhatsappActionManager(automation=automation)

        messages = whatsapp_action_manger.get_content('Moyo')
        print('\n---Message Result---')
        print(messages)

        summarized_chat = content_processor.summarize_chat(messages.data)
        print('\n---Processed result for summarizing chat---')
        print(summarized_chat)

        extracted_info = content_processor.extract_info(messages.data, query='Why did Moyo apologized')
        print('\n---Processed result for extracting info---')
        print(extracted_info)

        open_chat = whatsapp_action_manger.open_chat('Subomi Obans')
        print('\n---Action Result for opening message---')
        print(open_chat)

        send_message = whatsapp_action_manger.send_message(chat='Damisi', message="""Test message""")
        print('\n---Action Result for sending message---')
        print(send_message)


        page.pause()