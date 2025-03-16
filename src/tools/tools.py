from tools.calculator.calculator import calculate
from tools.command_runner.command_runner import run_command

DEFAULT_TOOLS = {
    "calculate": calculate,
}

ADMIN_TOOL = {
    "calculate": calculate,
    "command": run_command,
}