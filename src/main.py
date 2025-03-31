import logging
import sys
from agent.agent_anthropic_service import AgentAnthropicService
from agent.agent_openai_service import AgentOpenAIService
from core.config import ADMIN_USER_ROLE, DEFAULT_USER_ROLE, DOCKER_ENV_IDENTIFIER
from core.utils.logging import setup_logger

# disable when debugging
# logging.disable(logging.CRITICAL)

running_with_docker = len(sys.argv) > 1 and sys.argv[1] == DOCKER_ENV_IDENTIFIER
user_role = (
    ADMIN_USER_ROLE
    if len(sys.argv) > 2 and sys.argv[2] == ADMIN_USER_ROLE
    else DEFAULT_USER_ROLE
)


# TODO This is for the future, we will allow some command and os interactions with admin users
# if(user_role == DEFAULT_USER_ROLE):
# block_system_commands()
# enable if any critical interactions are added and if needed except argument validation

if __name__ == "__main__":
    logger = setup_logger()

    agent_openai_service = AgentOpenAIService()
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print(agent_openai_service.chat_with_model(user_input = user_input, user_role = user_role))
