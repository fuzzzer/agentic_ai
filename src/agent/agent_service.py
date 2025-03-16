

import abc
import abc
import json
import logging
from venv import logger

from agent.components.description import TOOLS_DESCRIPTION
from agent.components.tool_manager import execute_tool
from core.config import MODEL_NAME

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AgentService(abc.ABC):
    """
    Abstract base class that defines the common conversation and tool-calling loop.
    Subclasses must implement the _prepare_request and _stream_until_tool_or_end methods.
    """
    START_TOOL_IDENTIFIER = "[[tool]]"
    END_TOOL_IDENTIFIER = "[[/tool]]"

    def __init__(self, model_name=MODEL_NAME, tools_description=TOOLS_DESCRIPTION):
        self.model_name = model_name
        self.tools_description = tools_description
        # Conversation history as list of dicts with keys 'role' and 'content'
        self.conversation_history = [{"role": "system", "content": self.tools_description}]
        self.client = None  # Must be set by subclass

    def chat_with_model(self, user_input: str, user_role: str) -> str:
        """
        Main conversation loop:
          1. Append user input.
          2. Prepare request and stream response.
          3. If a tool command is detected, process it, add its result, and continue.
          4. Otherwise, return the final assistant response.
        """
        self.conversation_history.append({"role": "user", "content": user_input})
        last_answer = ""
        while True:
            request = self._prepare_request()
            answer, tool_command = self._stream_until_tool_or_end(request)
            if answer:
                self.conversation_history.append({"role": "assistant", "content": answer})
                last_answer = answer

            if tool_command is None:
                break

            tool_result = self._process_tool_command(tool_command, user_role)
            print(f"\n🔧 Tool Call Detected: {tool_command}")
            print(f"🔧 Tool Result: {tool_result}\n", flush=True)
            self.conversation_history.append({"role": "tool", "content": f"Tool result: {tool_result}"})
        return last_answer

    def _process_tool_command(self, command_str: str, user_role: str):
        """
        Parses and executes the tool command.
        """
        try:
            data = json.loads(command_str)
            if isinstance(data, dict) and "tool" in data:
                result = execute_tool(data, user_role)
                return result
            else:
                return "Invalid tool command (no 'tool' key)."
        except Exception as e:
            logger.error("nLOG: Error processing tool command: %s", e)
            return f"Error: {str(e)}"

    def _extract_tool_command(self, full_text: str):
        """
        Extracts a tool command from the provided text if present.
        Returns a tuple (start_index, tool_command_str) if found, otherwise (None, None).
        """
        end_idx = full_text.find(self.END_TOOL_IDENTIFIER)
        if end_idx != -1:
            start_idx = full_text.rfind(self.START_TOOL_IDENTIFIER, 0, end_idx)
            if start_idx != -1:
                tool_command_str = full_text[start_idx + len(self.START_TOOL_IDENTIFIER):end_idx].strip()
                return start_idx, tool_command_str
        return None, None

    @abc.abstractmethod
    def _prepare_request(self):
        """
        Converts the conversation history into the required request format.
        """
        pass

    @abc.abstractmethod
    def _stream_until_tool_or_end(self, request):
        """
        Streams the assistant’s response until a complete tool command is detected or the response ends.
        Returns (final_text, tool_command_str_or_None).
        """
        pass