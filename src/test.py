from tools.command_runner.command_runner import run_command_iterative

# Build arguments
args = {
    "command": "ls -la", 
    "working_dir": "/Users/fuzzzer/programming/AI_tools/agentic_ai/playground", 
    # If we wanted to feed interactive responses:
    "responses": []
}

result_json = run_command_iterative(args)
print(result_json)