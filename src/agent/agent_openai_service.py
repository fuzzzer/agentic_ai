import abc
import json
import logging
from venv import logger

from agent.agent_service import AgentService
from agent.components.description import TOOLS_DESCRIPTION
from agent.components.tool_manager import execute_tool
from core.config import API_BASE_URL, API_KEY, MODEL_NAME

from openai import OpenAI

class AgentOpenAIService(AgentService):
    def __init__(self, api_base_url=API_BASE_URL, api_key=API_KEY, model_name=MODEL_NAME, tools_description=TOOLS_DESCRIPTION):
        super().__init__(model_name=model_name, tools_description=tools_description)
        self.client = OpenAI(base_url=api_base_url, api_key=api_key)
        logger.info("nLOG: Initialized AgentOpenAIService with model: %s", self.model_name)

    def _prepare_request(self):
        """
        For OpenAI, the conversation history is already a list of dict messages.
        """
        return self.conversation_history

    def _stream_until_tool_or_end(self, messages):
        """
        Streams the response from OpenAI's API.
        """
        full_text = ""
        tool_command_str = None

        print("🤖 Assistant:", end="", flush=True)
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
                stop=[self.END_TOOL_IDENTIFIER]
            )
        except Exception as e:
            logger.error("nLOG: Error during chat completion creation: %s", e)
            print(" (Error fetching model output) ", e)
            return "(Model Error)", None

        for chunk in response:
            new_text = chunk.choices[0].delta.dict().get("content", "")
            if not new_text:
                continue

            print(new_text, end="", flush=True)
            full_text += new_text

        print()  # newline after streaming
        final_text, tool_command_str = self._extract_tool_command(full_text)
        return final_text, tool_command_str
