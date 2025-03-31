from tools.calculator.calculator import calculate
from tools.command_runner.command_runner import run_command
from tools.receipt_tracker.receipt_tracker import receipt_tracker

DEFAULT_TOOLS = {
    "calculate": calculate,
    "receipt_tracker": receipt_tracker,
}

ADMIN_TOOL = {
    "calculate": calculate,
    "receipt_tracker": receipt_tracker,
    "command": run_command,
}
