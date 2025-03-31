import json
import logging
import httpx
from agent.components.description import TOOLS_DESCRIPTION
from agent.components.tool_manager import execute_tool
from setup_config import API_BASE_URL, API_KEY, MODEL_NAME

# NOT BEING ACTIVELY MAINTAINED

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AgentHttpService:

    def __init__(
        self,
        base_url=API_BASE_URL,
        api_key=API_KEY,
        model_name=MODEL_NAME,
        tools_description=TOOLS_DESCRIPTION,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name
        self.tools_description = tools_description
        logger.info("nLOG: Initialized AgentService with model: %s", self.model_name)

    def build_payload(self, user_input):
        return {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.tools_description},
                {"role": "user", "content": user_input},
            ],
            "stream": True,
        }

    def send_chat_request(self, user_input):
        payload = self.build_payload(user_input)
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            with httpx.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0,
            ) as response:
                if response.status_code == 200:
                    return self.process_stream_response(response)
                else:
                    # Read the content before accessing it
                    content = response.read()
                    error_msg = (
                        f"❌ API Error: {response.status_code} - {content.decode()}"
                    )
                    logger.error(error_msg)
                    return error_msg
        except httpx.RequestError as e:
            error_msg = f"❌ Network Error: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def process_stream_response(self, response) -> str:
        full_response: str = ""
        logger.info("Starting to stream response...")
        print("🤖 Assistant:")

        for line in response.iter_lines():
            try:
                str_line: str = line
                json_str: str = (
                    str_line[len("data: ") :].strip()
                    if str_line.startswith("data: ")
                    else str_line.strip()
                )

                if json_str == "[DONE]" or not json_str:
                    continue

                parsed_line: dict = json.loads(json_str)

                if "choices" in parsed_line and len(parsed_line["choices"]) > 0:
                    delta_content: str = parsed_line["choices"][0]["delta"].get(
                        "content", ""
                    )
                    full_response += delta_content
                    print(delta_content, end="", flush=True)
            except json.JSONDecodeError as e:
                logger.error("Failed to parse JSON: " + str(e))
                continue

        print()
        return full_response

    def process_tool_calls(self, full_response, user_role):
        try:
            parsed_request = json.loads(full_response.strip())
            if (
                isinstance(parsed_request, dict)
                and "tool" in parsed_request
                and "args" in parsed_request
            ):
                result = execute_tool(parsed_request, user_role)
                return f"📌 Result: {result}"
        except json.JSONDecodeError:
            logger.info("Response does not contain a valid JSON tool command.")

        return f"(No tool detected)"

    def chat_with_model(self, user_input, user_role):
        full_response = self.send_chat_request(user_input)
        return self.process_tool_calls(full_response, user_role)
