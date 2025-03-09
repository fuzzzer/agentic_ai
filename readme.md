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
