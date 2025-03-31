# tools/file_manager/file_manager.py
import os
import json
import re
from typing import Dict, List, Any, Optional
from core.config import PERMITTED_OS_DIRECTORIES, FORBIDDEN_PATTERNS


class FileManager:
    """Handles file operations with strict path validation."""

    def __init__(self, allowed_dirs: List[str], forbidden_patterns: List[str]):
        """
        Initialize with allowed directories for operations.
        """
        self.allowed_dirs = [os.path.abspath(os.path.normpath(d)) for d in allowed_dirs]
        self.forbidden_patterns = forbidden_patterns

    def validate_path(self, path: str) -> Dict[str, Any]:
        """Validate if a path is within allowed directories."""
        if not path:
            return {"valid": False, "reason": "Empty path"}

        abs_path = os.path.abspath(os.path.normpath(path))

        # Check if path is in allowed directories
        for allowed_dir in self.allowed_dirs:
            if abs_path.startswith(allowed_dir):
                # Check for forbidden patterns in file path
                for pattern in self.forbidden_patterns:
                    if re.search(pattern, path):
                        return {
                            "valid": False,
                            "reason": f"Path matches forbidden pattern: {pattern}",
                        }
                return {"valid": True}

        return {"valid": False, "reason": f"Path not in allowed directories: {path}"}

    def validate_file_content(self, content: str) -> Dict[str, Any]:
        """Validate if file content contains forbidden patterns."""
        for pattern in self.forbidden_patterns:
            if re.search(pattern, content):
                return {
                    "valid": False,
                    "reason": f"Content matches forbidden pattern: {pattern}",
                }
        return {"valid": True}

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read the contents of a file after path validation."""
        path_validation = self.validate_path(file_path)
        if not path_validation["valid"]:
            return {"success": False, "error": path_validation["reason"]}

        if not os.path.isfile(file_path):
            return {"success": False, "error": f"File does not exist: {file_path}"}

        try:
            with open(file_path, "r") as f:
                content = f.read()

            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(
        self, file_path: str, content: str, create_dirs: bool = False
    ) -> Dict[str, Any]:
        """Write content to a file after path validation."""
        path_validation = self.validate_path(file_path)
        if not path_validation["valid"]:
            return {"success": False, "error": path_validation["reason"]}

        content_validation = self.validate_file_content(content)
        if not content_validation["valid"]:
            return {"success": False, "error": content_validation["reason"]}

        # Create parent directories if needed
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            if create_dirs:
                dir_validation = self.validate_path(dir_path)
                if not dir_validation["valid"]:
                    return {"success": False, "error": dir_validation["reason"]}

                try:
                    os.makedirs(dir_path, exist_ok=True)
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to create directories: {str(e)}",
                    }
            else:
                return {
                    "success": False,
                    "error": f"Parent directory does not exist: {dir_path}",
                }

        try:
            with open(file_path, "w") as f:
                f.write(content)

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_file(
        self, file_path: str, pattern: str, replacement: str
    ) -> Dict[str, Any]:
        """Update file content by replacing a pattern with new content."""
        read_result = self.read_file(file_path)
        if not read_result["success"]:
            return read_result

        content = read_result["content"]

        content_validation = self.validate_file_content(replacement)
        if not content_validation["valid"]:
            return {"success": False, "error": content_validation["reason"]}

        try:
            new_content, count = re.subn(pattern, replacement, content)

            write_result = self.write_file(file_path, new_content)
            if not write_result["success"]:
                return write_result

            return {"success": True, "matches": count}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_directory(self, dir_path: str) -> Dict[str, Any]:
        """List the contents of a directory after path validation."""
        path_validation = self.validate_path(dir_path)
        if not path_validation["valid"]:
            return {"success": False, "error": path_validation["reason"]}

        if not os.path.isdir(dir_path):
            return {"success": False, "error": f"Directory does not exist: {dir_path}"}

        try:
            entries = os.listdir(dir_path)
            files = [
                entry
                for entry in entries
                if os.path.isfile(os.path.join(dir_path, entry))
            ]
            directories = [
                entry
                for entry in entries
                if os.path.isdir(os.path.join(dir_path, entry))
            ]

            return {"success": True, "files": files, "directories": directories}
        except Exception as e:
            return {"success": False, "error": str(e)}


def file_operation(args: Dict[str, Any]) -> str:
    """Tool function to perform file operations with the FileManager."""

    if not isinstance(args, dict):
        return json.dumps({"error": "Invalid arguments"})

    operation = args.get("operation", "")
    file_path = args.get("file_path", "")
    dir_path = args.get("dir_path", "")
    content = args.get("content", "")
    pattern = args.get("pattern", "")
    replacement = args.get("replacement", "")
    create_dirs = args.get("create_dirs", False)

    if not operation:
        return json.dumps({"error": "No operation specified"})

    manager = FileManager(PERMITTED_OS_DIRECTORIES, FORBIDDEN_PATTERNS)

    if operation == "read":
        if not file_path:
            return json.dumps({"error": "No file path provided for read operation"})
        result = manager.read_file(file_path)

    elif operation == "write":
        if not file_path:
            return json.dumps({"error": "No file path provided for write operation"})
        result = manager.write_file(file_path, content, create_dirs)

    elif operation == "update":
        if not file_path:
            return json.dumps({"error": "No file path provided for update operation"})
        if not pattern:
            return json.dumps({"error": "No pattern provided for update operation"})
        result = manager.update_file(file_path, pattern, replacement)

    elif operation == "list":
        if not dir_path:
            return json.dumps(
                {"error": "No directory path provided for list operation"}
            )
        result = manager.list_directory(dir_path)

    else:
        result = {"error": f"Unsupported operation: {operation}"}

    return json.dumps(result)
