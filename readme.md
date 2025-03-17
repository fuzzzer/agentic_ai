add setup_config.py in src

eg:
API_BASE_URL = "http://localhost:1234/v1"
API_KEY = ""
MODEL_NAME = ""
REMOTE_MODEL_NAME = ""

ai_agent/
│── agent.py # The AI interface (interacts with LM Studio)
│── tool_manager.py # Routes tool requests securely
│── tools/
│ ├── **init**.py # Initializes the tools module
│ ├── calculator.py # Implements the calculator tool
│ ├── weather.py # Implements the weather tool
│── utils/
│ ├── security.py # Implements input validation and execution safety
│── config.py # Stores settings like API keys
│── main.py # Entry point to run the AI assistant
