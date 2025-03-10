import json
import ast
import re

def calculate(expression):
    try:
        expression = re.sub(r'(\d+)\s*\^\s*(\d+)', r'\1**\2', expression)
        
        node = ast.parse(expression, mode='eval')
        allowed_nodes = {
            ast.Expression, ast.BinOp, ast.UnaryOp,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
            ast.Constant  #(replaces ast.Num in newer Python versions)
        }

        for subnode in ast.walk(node):
            if type(subnode) not in allowed_nodes:
                return json.dumps({"error": "Invalid operation detected"})

        result = eval(expression, {"__builtins__": {}})
        return json.dumps({"result": result})

    except Exception as e:
        return json.dumps({"error": str(e)})
