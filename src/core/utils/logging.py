
# logging.basicConfig(
#     filename="logs/ai_tool_usage.log",
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )

def log_tool_request(tool_name, args):
    print(f"Tool Used: {tool_name}, Args: {args}")