import os
import json
import subprocess
import shlex
import re
from typing import Dict, List, Any, Optional


class CommandSession:
    """
    A session-based runner that lets you start a command, read its output
    iteratively, and optionally write input to stdin, then stop it.
    Can be used with or without AI for a "live" console experience.
    """
    def __init__(self, command: str, working_dir: Optional[str] = None):
        self.command = command
        self.working_dir = working_dir
        self.process = None

    def start(self):
        """Start the subprocess with pipes for stdout, stderr, stdin."""
        self.process = subprocess.Popen(
            shlex.split(self.command),
            cwd=self.working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True
        )

    def write_input(self, input_data: str):
        """Write string data (plus newline) to the command's stdin."""
        if self.process and self.process.stdin:
            self.process.stdin.write(input_data)
            self.process.stdin.flush()

    def read_stdout_lines(self):
        """Yield lines from stdout in real time (blocking until each line is available)."""
        if not self.process or not self.process.stdout:
            return
        for line in self.process.stdout:
            yield line

    def read_stderr_lines(self):
        """Yield lines from stderr in real time."""
        if not self.process or not self.process.stderr:
            return
        for line in self.process.stderr:
            yield line

    def is_running(self) -> bool:
        """Returns True if the subprocess is still running."""
        return self.process is not None and (self.process.poll() is None)

    def stop(self):
        """Terminate the process if it's still running."""
        if self.is_running():
            self.process.terminate()
            self.process.wait()


class CommandRunner:
    """Executes system commands with strict validation and sanitization."""
    
    def __init__(self, allowed_commands: List[str], allowed_dirs: List[str], 
                 forbidden_commands: List[str], forbidden_patterns: List[str]):
        """
        Initialize with security constraints defined by the application.
        """
        self.allowed_commands = allowed_commands
        self.allowed_dirs = [os.path.abspath(os.path.normpath(d)) for d in allowed_dirs]
        self.forbidden_commands = forbidden_commands
        self.forbidden_patterns = forbidden_patterns
    
    def validate_command(self, command: str) -> Dict[str, Any]:
        """Validate if a command is allowed to execute."""
        if not command:
            return {"valid": False, "reason": "Empty command"}
            
        try:
            parts = shlex.split(command)
        except ValueError as e:
            return {"valid": False, "reason": f"Invalid command format: {str(e)}"}
            
        if not parts:
            return {"valid": False, "reason": "Empty command after parsing"}
            
        executable = parts[0]
        
        # Check if the executable is allowed
        if executable not in self.allowed_commands:
            return {"valid": False, "reason": f"Command not allowed: {executable}"}
            
        # Check for forbidden commands
        for forbidden in self.forbidden_commands:
            if forbidden in command:
                return {"valid": False, "reason": f"Command contains forbidden element: {forbidden}"}
                
        # Check for forbidden patterns
        for pattern in self.forbidden_patterns:
            if re.search(pattern, command):
                return {"valid": False, "reason": f"Command matches forbidden pattern: {pattern}"}
        
        return {"valid": True}
    
    def validate_path(self, path: str) -> Dict[str, Any]:
        """Validate if a path is within allowed directories."""
        if not path:
            return {"valid": False, "reason": "Empty path"}
            
        abs_path = os.path.abspath(os.path.normpath(path))
        
        for allowed_dir in self.allowed_dirs:
            if abs_path.startswith(allowed_dir):
                return {"valid": True}
                
        return {"valid": False, "reason": f"Path not in allowed directories: {path}"}
    
    def execute(
        self, 
        command: str, 
        working_dir: Optional[str] = None, 
        interactive_responses: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a command after validation in a blocking manner.
        Returns stdout, stderr, and success status once the command finishes.
        """
        # Validate the command
        cmd_validation = self.validate_command(command)
        if not cmd_validation["valid"]:
            return {
                "success": False,
                "error": cmd_validation["reason"],
                "code": -1
            }
        
        # Validate the working directory
        if working_dir:
            if not os.path.isdir(working_dir):
                return {
                    "success": False,
                    "error": f"Working directory does not exist: {working_dir}",
                    "code": -1
                }
                
            path_validation = self.validate_path(working_dir)
            if not path_validation["valid"]:
                return {
                    "success": False,
                    "error": path_validation["reason"],
                    "code": -1
                }
        
        # Execute the command
        try:
            process = subprocess.Popen(
                shlex.split(command),
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE if interactive_responses else None,
                text=True
            )
            
            if interactive_responses:
                # Join responses with newlines and add a final newline
                input_data = "\n".join(interactive_responses) + "\n"
                stdout, stderr = process.communicate(input=input_data, timeout=30)
            else:
                stdout, stderr = process.communicate(timeout=30)
            
            return {
                "success": process.returncode == 0,
                "output": stdout,
                "error": stderr,
                "code": process.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command execution timed out",
                "code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code": -1
            }

def run_command_iterative(args: Dict[str, Any]) -> str:
    """
    Example function to show how you might use CommandSession iteratively.
    Validates the command similarly, then streams output line by line.
    Returns a summarized result in JSON.
    """
    from core.config import ALLOWED_OS_COMMANDS, PERMITTED_OS_DIRECTORIES, FORBIDDEN_COMMANDS, FORBIDDEN_PATTERNS
    
    if not isinstance(args, dict):
        return json.dumps({"error": "Invalid arguments"})
    
    command = args.get("command", "")
    working_dir = args.get("working_dir", None)
    interactive_inputs = args.get("responses", [])  # if we want to feed them while running
    
    # Basic validation (the same checks used in the standard execute)
    runner = CommandRunner(
        allowed_commands=ALLOWED_OS_COMMANDS,
        allowed_dirs=PERMITTED_OS_DIRECTORIES,
        forbidden_commands=FORBIDDEN_COMMANDS,
        forbidden_patterns=FORBIDDEN_PATTERNS
    )
    cmd_validation = runner.validate_command(command)
    if not cmd_validation["valid"]:
        return json.dumps({"success": False, "error": cmd_validation["reason"], "code": -1})
    
    # Validate working dir
    if working_dir and not os.path.isdir(working_dir):
        return json.dumps({"success": False, "error": f"Working directory does not exist: {working_dir}", "code": -1})
    
    if working_dir:
        path_validation = runner.validate_path(working_dir)
        if not path_validation["valid"]:
            return json.dumps({"success": False, "error": path_validation["reason"], "code": -1})
    
    # Now we do the iterative approach
    session = CommandSession(command=command, working_dir=working_dir)
    session.start()
    
    # If you need to feed initial interactive responses:
    for line_input in interactive_inputs:
        session.write_input(line_input + "\n")
    
    # Collect output
    stdout_lines = []
    stderr_lines = []
    
    # We'll keep reading until the process ends
    while session.is_running():
        # Read any available stdout lines
        for out_line in session.read_stdout_lines():
            stdout_lines.append(out_line)
            # You could print them in real-time or store them
            print(f"[STDOUT] {out_line}", end="")  # end="" because out_line has its own newline

        # Read any available stderr lines
        for err_line in session.read_stderr_lines():
            stderr_lines.append(err_line)
            print(f"[STDERR] {err_line}", end="")
    
    # The process has ended or was terminated
    returncode = session.process.returncode if session.process else -1
    
    return json.dumps({
        "success": (returncode == 0),
        "stdout": "".join(stdout_lines),
        "stderr": "".join(stderr_lines),
        "code": returncode
    })

def run_command(args: Dict[str, Any]) -> str:
    """
    Tool function to execute a command with the CommandRunner in a BLOCKING way
    (gathers all output, then returns).
    """
    from core.config import ALLOWED_OS_COMMANDS, PERMITTED_OS_DIRECTORIES, FORBIDDEN_COMMANDS, FORBIDDEN_PATTERNS
    
    if not isinstance(args, dict):
        return json.dumps({"error": "Invalid arguments"})
    
    command = args.get("command", "")
    working_dir = args.get("working_dir", None)
    responses = args.get("responses", None)
    
    if not command:
        return json.dumps({"error": "No command provided"})
    
    runner = CommandRunner(
        allowed_commands=ALLOWED_OS_COMMANDS,
        allowed_dirs=PERMITTED_OS_DIRECTORIES,
        forbidden_commands=FORBIDDEN_COMMANDS,
        forbidden_patterns=FORBIDDEN_PATTERNS
    )
    
    result = runner.execute(command, working_dir, responses)
    
    return json.dumps(result)
