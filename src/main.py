
import logging
import sys
from agent.agent_openai_service import AgentOpenAIService
from core.config import ADMIN_USER_ROLE, DEFAULT_USER_ROLE

#disable when debugging
logging.disable(logging.CRITICAL)

user_role = ADMIN_USER_ROLE if len(sys.argv) > 1 and sys.argv[1] == ADMIN_USER_ROLE else DEFAULT_USER_ROLE

#TODO This is for the future, we will allow some command and os interactions with admin users
# if(user_role == DEFAULT_USER_ROLE):
# block_system_commands()
# enable if any critical interactions are added and if needed except argument validation

if __name__ == "__main__":
    agent_openai_service = AgentOpenAIService()
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print(agent_openai_service.chat_with_model(user_input, user_role))


