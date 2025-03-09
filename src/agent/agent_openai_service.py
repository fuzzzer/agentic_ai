import json
import logging
from openai import OpenAI
from agent.description import TOOLS_DESCRIPTION
from agent.tool_manager import execute_tool
from core.config import API_BASE_URL, API_KEY, MODEL_NAME

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AgentOpenAIService:

    def __init__(self, api_base_url=API_BASE_URL, api_key=API_KEY,
                 model_name=MODEL_NAME, tools_description=TOOLS_DESCRIPTION):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.model_name = model_name
        self.tools_description = tools_description

        self.client = OpenAI(base_url=self.api_base_url, api_key=self.api_key)
        logger.info("Initialized AgentOpenAIService with model: %s", self.model_name)

    def build_messages(self, user_input):
        return [
            {"role": "system", "content": self.tools_description},
            {"role": "user", "content": user_input}
        ]

    def stream_chat(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True
            )
        except Exception as e:
            logger.error("Error during chat completion creation: %s", e)
            raise

        full_response = ""
        logger.info("Starting to stream response...")
        print("🤖 Assistant:")

        for chunk in response:
            try:
                delta = chunk.choices[0].delta
            except (AttributeError, IndexError) as e:
                logger.warning("Skipping malformed chunk: %s", e)
                continue

            token = delta.dict().get("content", "")
            if token:
                full_response += token
                print(token, end="", flush=True)

        print()
        logger.info("Completed streaming response.")
        return full_response

    def process_response(self, full_response, user_role):
        try:
            parsed_request = json.loads(full_response.strip())
            if isinstance(parsed_request, dict) and "tool" in parsed_request and "args" in parsed_request:
                result = execute_tool(parsed_request, user_role)
                return (
                    f"📌 Result: {result}"
                )
        except json.JSONDecodeError:
            logger.info("Response does not contain a valid JSON tool command.")

        return f"(No tool detected)"

    def chat_with_model(self, user_input, user_role):
        messages = self.build_messages(user_input)
        full_response = self.stream_chat(messages)
        return self.process_response(full_response, user_role)