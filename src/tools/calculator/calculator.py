import json
import ast

def calculate(expression):
    try:
        node = ast.parse(expression, mode='eval')
        allowed_nodes = {
            ast.Expression, ast.BinOp, ast.UnaryOp,
            ast.Add, ast.Sub, ast.Mult, ast.Div,
            ast.Constant  #(replaces ast.Num in newer Python versions)
        }

        for subnode in ast.walk(node):
            if type(subnode) not in allowed_nodes:
                return json.dumps({"error": "Invalid operation detected"})

        result = eval(expression, {"__builtins__": {}})
        return json.dumps({"result": result})

    except Exception as e:
        return json.dumps({"error": str(e)})
