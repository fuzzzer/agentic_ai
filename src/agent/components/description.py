# agent/components/description.py
TOOLS_DESCRIPTION = """
You have access to these tools, so you can use them to get exact answers:

1. **Calculator**  
   - Performs basic math calculations.  
   - Example usage: [[tool]]{"tool": "calculate", "args": "3+5*2"}[[/tool]]
   - Supported Operations: addition, subtraction, multiplication, division, exponents

2. **Weather**  
   - Retrieves current weather information.  
   - Example usage: [[tool]]{"tool": "weather", "args": ""}[[/tool]]

3. **Command Runner** (Admin only)
   - Execute system commands safely within allowed directories.
   - Example: [[tool]]{"tool": "command", "args": {"command": "ls -la", "working_dir": "/path/to/project"}}[[/tool]]
   - For interactive commands, provide responses array: 
     [[tool]]{"tool": "command", "args": {"command": "mason make super_remote_bricky", "working_dir": "/path/to/project", "responses": ["user_profile", "user_profile_data", "get_user_profile", "y"]}}[[/tool]]

4. **File Manager** (Admin only)
   - Perform operations on files within allowed directories.
   - Read a file: [[tool]]{"tool": "file", "args": {"operation": "read", "file_path": "/path/to/file"}}[[/tool]]
   - Write to a file: [[tool]]{"tool": "file", "args": {"operation": "write", "file_path": "/path/to/file", "content": "new content", "create_dirs": true}}[[/tool]]
   - Update a file: [[tool]]{"tool": "file", "args": {"operation": "update", "file_path": "/path/to/file", "pattern": "regex pattern", "replacement": "new text"}}[[/tool]]
   - List directory: [[tool]]{"tool": "file", "args": {"operation": "list", "dir_path": "/path/to/dir"}}[[/tool]]

IMPORTANT RULES:
- To call a tool, output exactly `[[tool]] <JSON> [[/tool]]`.  
- The JSON must have two keys: `"tool"` (name) and `"args"` (arguments).  
- Never provide raw JSON outside of `[[tool]]...[[/tool]]`.  
- Do not guess tool results. Wait for the actual result if you call a tool.  
- Answer directly if no tool is needed.
"""