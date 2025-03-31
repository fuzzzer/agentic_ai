import abc
import abc
import json
import logging
import re
from venv import logger

from agent.components.description import TOOLS_DESCRIPTION
from agent.components.tool_manager import execute_tool
from setup_config import MODEL_NAME

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
        self.conversation_history = [
            {"role": "system", "content": self.tools_description}
        ]
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
                self.conversation_history.append(
                    {"role": "assistant", "content": answer}
                )
                last_answer = answer

            if tool_command is None:
                break

            tool_result = self._process_tool_command(tool_command, user_role)
            print(f"\n🔧 Tool Call Detected: {tool_command}")
            print(f"🔧 Tool Result: {tool_result}\n", flush=True)
            logger.info(f"🔧 Tool Result: {tool_result}\n")
            self.conversation_history.append(
                {"role": "tool", "content": f"Tool result: {tool_result}"}
            )
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

        Returns a tuple (final_text, tool_command_str), where:
        - final_text: The text before the tool command.
        - tool_command_str: The extracted tool command (or None if not found).

        This logic assumes that the tool command starts after the START_TOOL_IDENTIFIER.
        Since Model API stops generation when the END_TOOL_IDENTIFIER is generated,
        the final prompt should contain text up to but not including that marker.
        """
        if self.START_TOOL_IDENTIFIER in full_text:
            parts = full_text.split(self.START_TOOL_IDENTIFIER, 1)
            final_text = parts[0]
            tool_command_str = parts[1].strip()
            return final_text, tool_command_str
        return full_text, None

    def _sanitize_tool_response(self, response: str) -> str:
        """Sanitize tool response to prevent context overflow."""
        max_length = 5000
        if len(response) > max_length:
            response = (
                response[:max_length]
                + f" [Output truncated, total length: {len(response)} characters]"
            )
        # Remove ANSI escape codes that may cause display issues
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", response)

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
