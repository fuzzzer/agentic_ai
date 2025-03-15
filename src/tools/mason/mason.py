import json
import os
import subprocess
import re
from typing import Dict, List, Any

def validate_directory(path: str, allowed_dirs: List[str]) -> bool:
    """Check if path is within allowed directories."""
    path = os.path.abspath(os.path.normpath(path))
    return any(path.startswith(os.path.abspath(os.path.normpath(d))) for d in allowed_dirs)

def execute_mason_command(args: Dict[str, Any]) -> str:
    """
    Execute Mason CLI commands and process the results.
    
    Args:
        command: Mason command to run
        allowed_dirs: List of directories where commands can run
        responses: List of responses for interactive prompts
        current_dir: Working directory for the command
    """
    if not isinstance(args, dict):
        return json.dumps({"error": "Invalid arguments"})
    
    command = args.get("command", "")
    allowed_dirs = args.get("allowed_dirs", [])
    responses = args.get("responses", [])
    current_dir = args.get("current_dir", os.getcwd())
    
    # Validate the command
    if not command.startswith("mason make "):
        return json.dumps({"error": "Only 'mason make' commands are supported"})
    
    # Validate the directory
    if not validate_directory(current_dir, allowed_dirs):
        return json.dumps({"error": f"Directory '{current_dir}' is not allowed"})
    
    # Execute the command
    try:
        process = subprocess.Popen(
            command.split(),
            cwd=current_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send responses to interactive prompts
        inputs = "\n".join(responses) + "\n"
        stdout, stderr = process.communicate(input=inputs)
        
        if process.returncode != 0:
            return json.dumps({
                "error": f"Command failed with code {process.returncode}",
                "output": stderr
            })
        
        # Extract generated files
        generated_files = detect_generated_files(current_dir, command.split()[-1], responses)
        
        return json.dumps({
            "success": True,
            "output": stdout,
            "generated_files": generated_files
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

def detect_generated_files(directory: str, brick_name: str, responses: List[str]) -> List[str]:
    """Detect files generated by Mason brick."""
    if brick_name == "super_remote_bricky" and len(responses) >= 2:
        service_name = responses[0]
        model_name = responses[1]
        
        expected_files = [
            f"{service_name}_cubit/{service_name}_cubit.dart",
            f"{service_name}_cubit/{service_name}_state.dart",
            f"data/data_sources/{service_name}_data_source.dart",
            f"data/models/{model_name}.dart",
            f"data/repositories/{service_name}_repositories.dart"
        ]
        
        # Return files that actually exist
        return [f for f in expected_files if os.path.exists(os.path.join(directory, f))]
    
    return []

def file_operations(args: Dict[str, Any]) -> str:
    """
    Perform file operations (read/write/modify) on generated files.
    
    Args:
        operation: "read", "write", or "update"
        file_path: Path to the file
        allowed_dirs: List of permitted directories
        content: New content (for write/update)
        pattern: Pattern to replace (for update)
        replacement: Replacement text (for update)
    """
    if not isinstance(args, dict):
        return json.dumps({"error": "Invalid arguments"})
    
    operation = args.get("operation", "")
    file_path = args.get("file_path", "")
    allowed_dirs = args.get("allowed_dirs", [])
    
    # Validate the file path
    file_path = os.path.abspath(os.path.normpath(file_path))
    if not validate_directory(file_path, allowed_dirs):
        return json.dumps({"error": f"File '{file_path}' is not in an allowed directory"})
    
    try:
        if operation == "read":
            if not os.path.exists(file_path):
                return json.dumps({"error": f"File '{file_path}' does not exist"})
            
            with open(file_path, 'r') as f:
                content = f.read()
            return json.dumps({"content": content})
            
        elif operation == "write":
            content = args.get("content", "")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
            return json.dumps({"success": True})
            
        elif operation == "update":
            if not os.path.exists(file_path):
                return json.dumps({"error": f"File '{file_path}' does not exist"})
                
            pattern = args.get("pattern", "")
            replacement = args.get("replacement", "")
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Perform the replacement
            if pattern:
                updated_content = re.sub(pattern, replacement, content)
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                    
            return json.dumps({"success": True})
            
        else:
            return json.dumps({"error": f"Unsupported operation: {operation}"})
            
    except Exception as e:
        return json.dumps({"error": str(e)})

def mason_tool(args: Dict[str, Any] = None) -> str:
    """Main entry point for the Mason tool."""
    if not args or not isinstance(args, dict):
        return json.dumps({"error": "Invalid arguments"})
    
    action = args.get("action", "")
    
    if action == "execute":
        return execute_mason_command(args)
    elif action == "file":
        return file_operations(args)
    else:
        return json.dumps({"error": f"Unsupported action: {action}"})