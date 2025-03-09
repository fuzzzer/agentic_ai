from core.config import ADMIN_USER_ROLE
from tools.tools import ADMIN_TOOL, DEFAULT_TOOLS


def is_valid_request(request, user_role: str):
    tools = ADMIN_TOOL if user_role == ADMIN_USER_ROLE else DEFAULT_TOOLS

    """Validates the structure and content of AI tool requests."""
    if not isinstance(request, dict):
        return False
    if "tool" not in request or "args" not in request:
        return False
    if request["tool"] not in  tools:
        return False
    return True

