from venv import logger
import anthropic

from agent.agent_service import AgentService
from agent.components.description import TOOLS_DESCRIPTION
from core.config import API_KEY, MODEL_NAME

class AgentAnthropicService(AgentService):
    def __init__(self, api_key=API_KEY, model_name=MODEL_NAME, tools_description=TOOLS_DESCRIPTION):
        super().__init__(model_name=model_name, tools_description=tools_description)
        self.client = anthropic.Anthropic(api_key=api_key)
        logger.info("\nLOG: Initialized AgentAnthropicService with model: %s", self.model_name)

    def _prepare_request(self):
        role_prefix = {
            "system": "System:",
            "user": "Human:",
            "assistant": "Assistant:",
            "tool": "Tool:"
        }
        lines = []
        for msg in self.conversation_history:
            prefix = role_prefix.get(msg["role"], msg["role"])
            lines.append(f"{prefix} {msg['content']}")
        # Append the Assistant marker to prompt new completion
        lines.append("Assistant:")
        return "\n".join(lines)

    def _stream_until_tool_or_end(self, prompt: str):
        """
        Streams Anthropic's response and stops when the closing tool marker is encountered.
        Since we set stop_sequences to [[/tool]], Anthropic stops generation as soon as it’s about
        to output that token. We then inspect the generated text:
         - If a tool command is present (i.e. the start marker exists), we extract everything 
           after [[tool]] as the tool command.
         - The final assistant output is considered to be everything before the tool command.
        """
        full_text = ""
        tool_command_str = None
        print("🤖 Assistant:", end="", flush=True)
        # Instruct Anthropic to stop if the END_TOOL_IDENTIFIER is encountered.
        stop_sequences = [self.END_TOOL_IDENTIFIER]
        try:
            response = self.client.completions.create(
                model=self.model_name,
                prompt=prompt,
                max_tokens=300,
                stream=True,
                stop_sequences=stop_sequences
            )
        except Exception as e:
            logger.error("\nLOG: Error during chat completion creation: %s", e)
            print(" (Error fetching model output) ")
            return "(Model Error)", None

        for chunk in response:
            new_text = chunk.get("completion", "")
            if not new_text:
                continue

            print(new_text, end="", flush=True)
            full_text += new_text

            # Since the model stops at the end marker, we now check if there's a tool command.
            # If the start marker exists in full_text, we assume it's a tool call.
            if self.START_TOOL_IDENTIFIER in full_text:
                parts = full_text.split(self.START_TOOL_IDENTIFIER, 1)
                final_text = parts[0]
                tool_command_str = parts[1].strip()  # may be incomplete if the end marker was not generated
                # Note: Because stop_sequences stops generation at [[/tool]],
                # full_text should contain text up to but not including the closing marker.
                break

        print()  # newline after streaming
        if tool_command_str is not None:
            return final_text, tool_command_str
        else:
            return full_text, None
