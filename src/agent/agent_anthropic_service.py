import json
from venv import logger
import anthropic
import logging
import re
from typing import Tuple, Optional

from agent.agent_service import AgentService
from agent.components.description import TOOLS, TOOLS_DESCRIPTION
from setup_config import API_KEY, REMOTE_MODEL_NAME

class AgentAnthropicService(AgentService):
    def __init__(self, api_key=API_KEY, model_name=REMOTE_MODEL_NAME, tools_description=TOOLS_DESCRIPTION):
        super().__init__(model_name=model_name, tools_description=tools_description)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized AgentAnthropicService with model: {self.model_name}")
        self.tools = TOOLS

    def _sanitize_tool_response(self, response: str) -> str:
        """Sanitize tool response to prevent context overflow."""
        max_length = 5000
        if len(response) > max_length:
            response = response[:max_length] + f" [Output truncated, total length: {len(response)} characters]"
        # Remove ANSI escape codes that may cause display issues
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', response)

    def _prepare_request(self):
        """
        Convert conversation history to Anthropic's format.
        Constructs a messages-based API request for Claude 3.
        """
        # Use the system message if available, otherwise fall back to the tools description.
        system_message = next(
            (msg["content"] for msg in self.conversation_history if msg["role"] == "system"),
            self.tools_description
        )

        print('history length', len(self.conversation_history))


        messages = []
        for msg in self.conversation_history:
            if msg["role"] == "system":
                continue
            else:
                messages.append({"role": msg["role"], "content": msg["content"]})

        request_data = {
            "system": system_message,
            "messages": messages
        }
        self.logger.debug(f"Prepared request data: {request_data}")
        return request_data

    def _stream_until_tool_or_end(self, request_data) -> Tuple[str, Optional[str]]:
        """
        Streams the response from Claude while detecting and extracting tool calls.
        Returns a tuple of (assistant_response, tool_command_json_string).
        
        This implementation follows Anthropic’s guidelines (Clause 3.7) by correctly
        parsing tool use responses as they stream.
        """
        full_text = ""
        full_tool_str = ""
        collecting_tool_use = False
        stop_reason = ""


        print("🤖 Assistant:", end="", flush=True)       

        try:
            response = self.client.messages.create(
                model=self.model_name,
                system=request_data["system"],
                messages=request_data["messages"],
                max_tokens=30024,
                temperature=0.7,
                tools=self.tools,
                stream=True
            )

            for chunk in response:
                delta = getattr(chunk, "delta", None)
                if delta is None:
                    continue

                text_chunk = getattr(delta, "text", None)
                if text_chunk:
                    print(text_chunk, end="", flush=True)
                    full_text += text_chunk
                
                tool_command_chunk = getattr(delta, "partial_json", None)
                if tool_command_chunk:
                    if not collecting_tool_use:
                        print() # adding new line before tool use print
                        collecting_tool_use = True
                    print(tool_command_chunk, end="", flush=True)
                    full_tool_str += tool_command_chunk

                if getattr(chunk, "stop_reason", None):
                    stop_reason = getattr(chunk, "stop_reason", None)

                if getattr(chunk, "usage", None):
                    stop_reason = "usage"
                    break

            print()  # New line after streaming completes.

            # If tool use data was collected, format it as a tool command.
            if collecting_tool_use and full_tool_str:
                try:
                    parsed_tool = json.loads(full_tool_str)
                    tool_as_key = list(parsed_tool.keys())[0]
                    args = parsed_tool[tool_as_key]

                    if tool_as_key == "command":
                        full_tool_str = json.dumps({
                            "tool": "command",
                            "args": {
                                "command": args,
                                "working_dir": "/app",
                            }
                        })
                    else:
                        full_tool_str = json.dumps({
                            "tool": tool_as_key,
                            "args": args
                        })

                    self.logger.info(f"Tool detected: {full_tool_str}")
                    return full_text, full_tool_str
                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parsing tool input: {e}")

        except Exception as e:
            self.logger.error(f"Error during chat completion: {e}")
            print(f" (Error fetching model output: {e}) ")
            return f"(Model Error: {e})", None

        return full_text, None

    def chat_with_model(self, user_input: str, user_role: str) -> str:
        """
        Enhanced version that properly handles iterative tool usage with the Claude API.
        """
        self.conversation_history.append({"role": "user", "content": user_input})
        last_answer = ""
        max_iterations = 20  # Prevent infinite loops.
        iterations = 0

        while iterations < max_iterations:
            iterations += 1
            request_data = self._prepare_request()
            answer, tool_command = self._stream_until_tool_or_end(request_data)

            if answer and answer.strip():
                self.conversation_history.append({"role": "assistant", "content": answer})
                last_answer = answer

            if not tool_command:
                break

            # Process the tool call.
            try:
                self.logger.info(f"Processing tool command: {tool_command}")
                tool_result = self._process_tool_command(tool_command, user_role)
                sanitized_result = self._sanitize_tool_response(tool_result)

                print(f"\n🔧 Tool Call Detected: {tool_command}")
                print(f"🔧 Tool Result: {sanitized_result}\n", flush=True)

                # Add tool result to conversation history.
                self.conversation_history.append({
                    "role": "user",
                    "content": f"Tool result: {sanitized_result}"
                })

            except Exception as e:
                error_msg = f"Error processing tool command: {e}"
                self.logger.error(error_msg)
                self.conversation_history.append({
                    "role": "user",
                    "content": f"Tool execution error: {error_msg}"
                })
                break  # Stop processing on error.

        if iterations >= max_iterations:
            self.logger.warning("Reached maximum number of tool use iterations")

        self.logger.info(f"Returning final answer from chat_with_model: {last_answer}")
        return last_answer
