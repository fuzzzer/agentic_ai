import abc
import json
import logging
from venv import logger

from agent.agent_service import AgentService
from agent.components.description import LM_STUDIO_TOOLS, RECEIPT_TRACKER_DESCRIPTION, TOOLS_DESCRIPTION
from agent.components.tool_manager import execute_tool
from setup_config import API_BASE_URL, API_KEY, MODEL_NAME

from openai import OpenAI

class AgentOpenAIService(AgentService):
    def __init__(self, api_base_url=API_BASE_URL, api_key=API_KEY, model_name=MODEL_NAME, tools_description=RECEIPT_TRACKER_DESCRIPTION):
        super().__init__(model_name=model_name, tools_description=tools_description)
        self.client = OpenAI(base_url=api_base_url, api_key=api_key)
        self.tools = LM_STUDIO_TOOLS
        logger.info("nLOG: Initialized AgentOpenAIService with model: %s", self.model_name)

    def _prepare_request(self):
        """
        We follow open ai conversation like history so override is needed.
        """
        return self.conversation_history

    def _stream_until_tool_or_end(self, messages):
        """
        Streams the response from LM Studio API
        """
        full_text = ""
        full_tool_call_str = ""

        print("🤖 Assistant:", end="", flush=True)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
                # tools=self.tools,
                stop=[self.END_TOOL_IDENTIFIER]
            )

            print('print 1')

            for chunk in response:
                    delta = getattr(chunk.choices[0], "delta", None)
                    if delta is None:
                        continue

                    text_chunk = getattr(delta, "content", None)
                    if text_chunk:
                        print(text_chunk, end="", flush=True)
                        full_text += text_chunk
                                        
                    tool_calls = getattr(delta, "tool_calls", None)
                    if tool_calls:
                        if not full_tool_call_str:
                            print() # adding new line before starting tool command writing
                        function = getattr(tool_calls[0], "function", None)
                        tool_call_chunk = getattr(function, "arguments", None)
                        print(tool_call_chunk, end="", flush=True)
                        full_tool_call_str += tool_call_chunk

            if full_tool_call_str:
                    try:
                        parsed_tool = json.loads(full_tool_call_str)
                        tool_as_key = list(parsed_tool.keys())[0]
                        args = parsed_tool[tool_as_key]

                        if tool_as_key == "command":
                            full_tool_call_str = json.dumps({
                                "tool": "command",
                                "args": {
                                    "command": args,
                                    "working_dir": "/app",
                                }
                            })
                        else:
                            full_tool_call_str = json.dumps({
                                "tool": tool_as_key,
                                "args": args
                            })

                        logger.info(f"Tool detected: {full_tool_call_str}")
                        return full_text, full_tool_call_str
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing tool input: {e}")

        except Exception as e:
            logger.error("nLOG: Error during chat completion creation: %s", e)
            print(" (Error fetching model output) ", e)
            return "(Model Error)", None

        print()  # newline after streaming
        if not full_tool_call_str:
            full_text, full_tool_call_str = self._extract_tool_command(full_text) #check for any tool identifiers for the models that manually use tools

        return full_text, full_tool_call_str
    
    def chat_with_model(self, user_input: str, user_role: str) -> str:
        """
        Enhanced version that properly handles iterative tool usage with the Claude API.
        """
        self.conversation_history.append({"role": "user", "content": user_input})
        last_answer = ""
        max_iterations = 1
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
                logger.info(f"Processing tool command: {tool_command}")
                tool_result = self._process_tool_command(tool_command, user_role)
                sanitized_result = self._sanitize_tool_response(tool_result)

                print(f"\n🔧 Tool Call Detected: {tool_command}")
                print(f"🔧 Tool Result: {sanitized_result}\n", flush=True)

                # Add tool result to conversation history.
                self.conversation_history.append({
                    "role": "tool",
                    "content": f"Tool result: {sanitized_result}"
                })

            except Exception as e:
                error_msg = f"Error processing tool command: {e}"
                logger.error(error_msg)
                self.conversation_history.append({
                    "role": "tool",
                    "content": f"Tool execution error: {error_msg}"
                })
                break  # Stop processing on error.

        if iterations >= max_iterations:
            logger.warning("Reached maximum number of tool use iterations")

        logger.info(f"Returning final answer from chat_with_model: {last_answer}")
        return last_answer

