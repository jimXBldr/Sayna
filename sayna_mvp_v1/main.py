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
        messages = whatsapp_action_manger.get_content('Subomi Obans')
        print(messages)
        page.pause()