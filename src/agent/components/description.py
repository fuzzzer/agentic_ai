TOOLS_DESCRIPTION = """
You have access to these tools, so you can use them to get exact answers:

1. **Calculator**  
   - Performs basic math calculations.  
   - Example usage: [[tool]]{"tool": "calculate", "args": "3+5*2"}[[/tool]]
   - Supported Operations: ast.Expression, ast.BinOp, ast.UnaryOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,

2. **Weather**  
   - Retrieves current weather information.  
   - Example usage: [[tool]]{"tool": "weather", "args": ""}[[/tool]]

IMPORTANT RULES:
- To call a tool, output exactly `[[tool]] <JSON> [[/tool]]`.  
- The JSON must have two keys: `"tool"` (name) and `"args"` (arguments).  
- Never provide raw JSON outside of `[[tool]]...[[/tool]]`.  
- Do not guess tool results. Wait for the actual result if you call a tool.  
- Answer directly if no tool is needed.
"""
