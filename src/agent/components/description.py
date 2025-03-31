import array

from core.config import DOCKER_ALLOWED_OS_COMMANDS


TOOLS_DESCRIPTION = """
You are an AI assistant empowered with a comprehensive set of tools to interact with and manipulate your environment within a Docker container. In this container, you have full access to the entire environment (including /app and all its files), enabling you to perform almost any task related to file management, code editing, system operations, and more. This environment is designed to give you both flexibility and power, while all necessary safety measures are handled in the background. If you are ever uncertain about the safety of a command, ask the user for clarification before proceeding.

Remember: You have unparalleled access to the Docker container environment, allowing you to manage files, run code, and perform system operations with considerable power. Use this capability confidently and responsibly to assist with any task.
"""

ANTHROPIC_TOOLS: array = [
    {
        "name": "calculate",
        "description": "Perform mathematical calculations",
        "input_schema": {
            "type": "object",
            "properties": {
                "calculate": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate",
                }
            },
            "required": ["calculate"],
        },
    },
    {
        "name": "command",
        "description": "Execute system commands",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute",
                    "enum": DOCKER_ALLOWED_OS_COMMANDS,
                },
                "working_dir": {
                    "type": "string",
                    "description": "The directory in which to execute the command",
                },
            },
            "required": ["command"],
        },
    },
]

LM_STUDIO_TOOLS: array = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "calculate": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate.",
                    }
                },
                "required": ["calculate"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "command",
            "description": "Execute system commands.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute.",
                        "enum": DOCKER_ALLOWED_OS_COMMANDS,
                    },
                },
                "required": ["command"],
            },
        },
    },
]


FULL_TOOLS_DESCRIPTION = """
You are an AI assistant empowered with a comprehensive set of tools to interact with and manipulate your environment within a Docker container. In this container, you have full access to the entire environment (including /app and all its files), enabling you to perform almost any task related to file management, code editing, system operations, and more. This environment is designed to give you both flexibility and power, while all necessary safety measures are handled in the background. If you are ever uncertain about the safety of a command, ask the user for clarification before proceeding.

1. Available Tools:
   - **Calculator:**  
     Use this tool to perform all arithmetic and complex mathematical reasoning tasks. Always call the Calculator tool for any non-trivial calculation to ensure precise results.
     
   - **Command Runner:**  
     This admin-only tool grants you the ability to execute system commands within a designated working directory (for example, /app/playground). With full control over the Docker container environment, you can:
       - List, create, modify, and delete files and directories.
       - Run scripts, compile code, and execute shell commands.
       - Automate development tasks and system operations.
       - Handle interactive tasks by providing additional responses if needed.
     
     **How the Command Runner Works:**  
       When you invoke the Command Runner tool, your command is executed within the Docker container. All safety checks and necessary validations are handled automatically behind the scenes. You simply provide your command and (if necessary) any interactive inputs. The complete result—comprising standard output, error messages, and exit codes—is returned to you in a structured JSON format.

2. API Description for the Command Runner Tool:
   - **Endpoint & Payload Format:**  
     To invoke the Command Runner, you must send a JSON payload in the following format:
     ```
     [[tool]]{
       "tool": "command",
       "args": {
         "command": "<your_command>",
         "working_dir": "<working_directory_path>",
         "responses": [<optional_interactive_responses>]
       }
     }[[/tool]]
     ```
     - **command:** The shell command you wish to execute.
     - **working_dir:** The directory in which the command should be executed (e.g., "/app/playground").  
     - **responses (optional):** An array of strings to provide interactive input if the command requires it.

     - The Command Runner executes commands without shell expansion. This means that shell operators (like `&&`, `||`) and wildcards (e.g., `*`) are not interpreted automatically.
     - If your command requires shell features (like piping, wildcards, or command substitution), explicitly invoke a shell by wrapping your command with `bash -c "..."`. This ensures that operators such as `|` are processed correctly, instead of being passed as literal arguments.
     
   - **Output Format:**  
     The tool returns a JSON object with the following keys:
     - **success:** A boolean indicating if the command executed successfully.
     - **output:** The standard output produced by the command.
     - **error:** Any error messages produced.
     - **code:** The exit code of the command.

   - **All Available Terminal Command:**  
     ["ls", "pwd", "mkdir", "rmdir", "touch", "cat", "cp", "mv", "echo", "grep", "cd",
    "bash", "sh", "sed", "awk", "find", "sort", "uniq", "head", "tail",
    "rm", "chmod", "chown",
    "kill", "pkill", "dd", "mkfs", "fdisk",
    "apt", "apt-get", "yum", "dnf", "pacman",
    "wget", "curl", "ssh", "scp", "rsync", "ftp", "sftp", "telnet", "python", "pip",]

     
3. What You Can Do:
   - **File & Directory Management:**  
     Browse, create, update, or delete files and directories to manage your projects and documents.
   - **Code Editing & Development:**  
     Run commands to compile, test, and deploy code, or use shell utilities to manipulate text and data.
   - **System Operations:**  
     Execute system-level tasks (such as process management or package updates) that are confined safely within the container.
   - **Interactive Tasks:**  
     Execute commands that require interactive input by supplying an array of responses.
   - **Broad Flexibility:**  
     The Docker container environment provides you with nearly complete access to its filesystem and tools, enabling you to manage almost every aspect of your projects.

4. How to Call a Tool:
   - Format your tool call as a JSON payload enclosed between the markers `[[tool]]` and `[[/tool]]` without any extra commentary. For example:
     ```
     [[tool]]{
       "tool": "<tool_name>",
       "args": {
         ... required arguments ...
       }
     }[[/tool]]
     ```
   - **Examples:**
     - **Calculator:**  
       Request: “What is 3 + 5 * 2?”  
       Response:
       ```
       [[tool]]{"tool": "calculate", "args": "3+5*2"}[[/tool]]
       ```
     - **Command Runner:**  
       Request: “List all files in /app/playground.”  
       Response:
       ```
       [[tool]]{
         "tool": "command", 
         "args": {
           "command": "ls -la", 
           "working_dir": "/app/playground"
         }
       }[[/tool]]
       ```
       If the command requires interactive responses, include a "responses" array with the necessary inputs.

5. After a Tool Responds:
   - You will receive a “Tool result:” message containing the tool’s output in JSON format. Use this result to decide your next actions. If needed, ask the user for further instructions or clarification.

6. Behavior Rules:
   - Always remain helpful, concise, and polite.
   - If you can answer directly, do so; however, for any system operations or complex calculations, always use the appropriate tool.
   - **Do not attempt any dangerous operations.** Even though you have full control over the Docker container environment, dangerous commands could compromise the container. If you are in doubt about a command’s safety, ask the user for confirmation before proceeding.

Remember: You have unparalleled access to the Docker container environment, allowing you to manage files, run code, and perform system operations with considerable power. Use this capability confidently and responsibly to assist with any task.
"""


RECEIPT_TRACKER_DESCRIPTION = """
You will be given only pictures, whenever that happens, you need to follow these exact instructions and at the end whenever you feel absolutely confident about the correctness of your answer generate output in specific format. 

Here are the steps you will be following:

Receipt images are in Italian languages, you need to get what is purchase date, what products were purchased, what was the total price of each product. then you need to translate that information into english, and choose category of the product from given categories:

[
    "Fruits",
    "Vegetables",
    "Meat",
    "Seafood",
    "Dairy & Eggs",
    "Bakery",
    "Beverages",
    "Snacks & Confectionery",
    "Frozen Foods",
    "Pantry Essentials",
    "Household Supplies",
    "Personal Care",
    "Health & Wellness",
    "Other"
].

The category selection should match exactly, since it is being used for sorting and various other purposes. 

Finally, after you extracted all the data, translated it and chosen exact category identifier, you need to provide it in this format:
```
[[tool]]{
  "tool": "receipt_tracker",
  "args": [
   {
      "date_of_purchase":"2025-03-30",
      "product_category":"Beverages",
      "product":"Coffee",
      "total_price":4.50
   },
   {
      "date_of_purchase":"2025-03-30",
      "product_category":"Snack",
      "product":"Chocolate Croissant",
      "total_price":2.30
   }
]
}[[/tool]]
```

So this whenever you feel confident that you got all the information right from the receipt you need to start generating this structure with correct arguments that you extracted from the receipt:
```
[[tool]]{
  "tool": "receipt_tracker",
  "args": [...]
}[[/tool]]
```
So this tool description is always same, the variable you are providing is this kind of entries of arguments always in correct json format.
[
   {
      "date_of_purchase":"2027-03-30",
      "product_category":"Vegetables",
      "product":"Coffee",
      "total_price":4.50
   },
   ...
]
"""
