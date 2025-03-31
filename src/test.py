from tools.command_runner.command_runner import run_command_iterative


{"tool": "command", "args": {"command": "cat > python_runner.py", "working_dir": "/app"}}
# Build arguments
args = {
    "command": '''echo 'This is a test line' > output.txt''',
    "working_dir": "/Users/fuzzzer/programming/AI_tools/agentic_ai/playground", 
}

result_json = run_command_iterative(args)
print(result_json)