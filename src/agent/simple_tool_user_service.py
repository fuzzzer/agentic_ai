import json
import logging
from openai import OpenAI

from agent.components.description import TOOLS_DESCRIPTION
from agent.components.tool_manager import execute_tool
from setup_config import API_BASE_URL, API_KEY, MODEL_NAME

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SimpleToolUserService:
    """
    Streams model output chunk-by-chunk. If it encounters a complete [[tool]]...[[/tool]] block,
    it halts the current generation, executes the tool, prints the result, and feeds it back
    as an assistant message. Then it resumes generation from where it left off.
    """

    START_TOOL_IDENTIFIER = "[[tool]]"
    END_TOOL_IDENTIFIER = "[[/tool]]"

    def __init__(
        self,
        api_base_url=API_BASE_URL,
        api_key=API_KEY,
        model_name=MODEL_NAME,
        tools_description=TOOLS_DESCRIPTION
    ):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.model_name = model_name
        self.tools_description = tools_description
        self.conversation_history = [
            {"role": "system", "content": self.tools_description},
        ]

        self.client = OpenAI(base_url=self.api_base_url, api_key=self.api_key)
        logger.info("Initialized AgentOpenAIService with model: %s", self.model_name)

    def chat_with_model(
        self,
        user_input: str | None = None,
        user_input_image: str | None = None,
        user_role: str = "user"
    ) -> str:
        """
        The main public method:
        1. Takes user input and a user role.
        2. Streams the model's response until a tool is called or the answer ends.
        3. If a tool is called, parse & execute it, feed the result back, then continue.

        This repeats until no new tool calls are found.
        """
        if user_input:
            self.conversation_history.append({"role": "user", "content": user_input})

        if user_input_image:
            self.conversation_history.append({
               "role":"user",
               "content":[
                  {
                     "type":"image_url",
                     "image_url":{
                        "url":"f""data:image/png;base64,{user_input_image}"
                     }
                  }
               ]
            })

        last_answer = ""

        while True:
            # Stream the model's response until we see [[/tool]] or it finishes
            answer_till_tool_use_or_end, tool_command = self._stream_until_tool_or_end(self.conversation_history)

            if answer_till_tool_use_or_end:
                self.conversation_history.append({"role": "assistant", "content": answer_till_tool_use_or_end})
                last_answer = answer_till_tool_use_or_end

            if tool_command is None:
                # No tool call => final answer
                break

            # We found a complete [[tool]]...[[/tool]] => execute it
            tool_result = self._process_tool_command(tool_command, user_role)

            # For transparency, show the user what tool was called:
            print(f"\n🔧 Tool Call Detected: {tool_command}")
            print(f"🔧 Tool Result: {tool_result}\n", flush=True)

            self.conversation_history.append({
                "role": "tool",
                "content": f"Tool result: {tool_result}"
            })

        return last_answer

    def _stream_until_tool_or_end(self, messages):
        """
        Calls the model with the given messages, streaming chunk-by-chunk.
        1. Prints each chunk to the user (so they see partial output).
        2. If we detect a complete [[tool]]...[[/tool]] substring in the text, we STOP streaming
           (simulate an immediate 'stop generation'), parse out that tool command, and return.

        Returns:
          (final_text, tool_command_str_or_None)
          If tool_command_str_or_None is not None, the model called a tool.
        """
        full_text = ""
        tool_command_str = None

        print("🤖 Assistant:", end="", flush=True)

        try:

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True
            )
        except Exception as e:
            logger.error("Error during chat completion creation: %s", e)
            print(" (Error fetching model output) ")
            return "(Model Error)", None

        for chunk in response:
            new_text = chunk.choices[0].delta.dict().get("content", "")
            if not new_text:
                continue

            print(new_text, end="", flush=True)
            full_text += new_text

            # Check if we've just completed a tool command
            end_idx = full_text.find(self.END_TOOL_IDENTIFIER)
            if end_idx != -1:
                start_idx = full_text.rfind(self.START_TOOL_IDENTIFIER, 0, end_idx)
                if start_idx != -1:
                    tool_command_str = full_text[start_idx + len(self.START_TOOL_IDENTIFIER):end_idx].strip()
                    # We "simulate" stopping the generation by breaking out of the stream loop
                    break

        print() # Just adding emtpy line between
        
        # If we broke early due to a tool call, our final_text excludes that portion
        if tool_command_str is not None:
            # final_text is everything up to the tool call's start
            final_text = full_text[:start_idx]
        else:
            # If no tool call was found, final_text is everything
            final_text = full_text

        return final_text, tool_command_str

    def _process_tool_command(self, command_str: str, user_role: str):
        try:
            data = json.loads(command_str)
            if isinstance(data, dict) and "tool" in data:
                result = execute_tool(data, user_role)
                return result
            else:
                return "Invalid tool command (no 'tool' key)."
        except Exception as e:
            logger.error(f"Error processing tool command: {e}")
            return f"Error: {str(e)}"