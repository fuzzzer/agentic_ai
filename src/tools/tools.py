from tools.calculator.calculator import calculate
from tools.command_runner.command_runner import run_command
from tools.receipt_tracker.receipt_tracker import receit_tracker

DEFAULT_TOOLS = {
    "calculate": calculate,
    "receit_tracker": receit_tracker,
}

ADMIN_TOOL = {
    "calculate": calculate,
    "receit_tracker": receit_tracker,
    "command": run_command,
}