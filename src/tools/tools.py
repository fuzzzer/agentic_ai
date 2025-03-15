from tools.calculator.calculator import calculate
from tools.weather.weather import get_weather
from tools.command_runner.command_runner import run_command
from tools.file_manager.file_manager import file_operation

DEFAULT_TOOLS = {
    "calculate": calculate,
    "weather": get_weather,
}

ADMIN_TOOL = {
    "calculate": calculate,
    "weather": get_weather,
    "command": run_command,
    "file": file_operation,
}