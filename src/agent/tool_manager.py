import json
from core.config import ADMIN_USER_ROLE
from core.utils.logging import log_tool_request
from core.utils.validation import is_valid_request
from tools.tools import ADMIN_TOOL, DEFAULT_TOOLS


def execute_tool(request, user_role):
    if not is_valid_request(request, user_role):
        return json.dumps({"error": "Invalid request format or unauthorized tool access."})
    
    tool_name = request["tool"]
    args = request["args"]
    # TODO add argument validation and restriction of arguments with some dangerous phrazes, or allowing only custom arguments

    log_tool_request(tool_name, args)

    if(user_role == ADMIN_USER_ROLE):
        return execute_admin_tool(tool_name, args)
    
    return execute_default_tool(tool_name, args)


def execute_admin_tool(tool_name, args):
    if tool_name not in ADMIN_TOOL:
        return json.dumps({"error": "Unauthorized tool access"})

    return ADMIN_TOOL[tool_name](args) if args else ADMIN_TOOL[tool_name]()


def execute_default_tool(tool_name, args):
    if tool_name not in DEFAULT_TOOLS:
        return json.dumps({"error": "Unauthorized tool access"})

    return DEFAULT_TOOLS[tool_name](args) if args else DEFAULT_TOOLS[tool_name]()
