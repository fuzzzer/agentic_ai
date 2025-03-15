import os


API_BASE_URL = "http://127.0.0.1:1234/v1"
API_KEY = "lm-studio"
MODEL_NAME = "dolphin3.0-qwen2.5-3b"
DEFAULT_USER_ROLE = "basic"
ADMIN_USER_ROLE = "admin"

## Be very careful when we permit ai to do some changes or run some commands in some directory
PERMITTED_OS_DIRECTORIES = [
    os.path.expanduser("~/programming/AI_tools/agentic_ai")  
]

ALLOWED_OS_COMMANDS = [
    "ls", "pwd", "mkdir", "rmdir", "touch", "cat", "cp", "mv", "echo", "grep",
    "mason",
    "flutter",
    "dart",
]

FORBIDDEN_COMMANDS = [
    "sudo", "su", "rm", "rmdir", "chmod", "chown", "kill", "pkill",
    "reboot", "shutdown", "halt", "poweroff", "init", "mount", "umount", 
    "dd", "mkfs", "fdisk", "iptables", "systemctl", "service",
    "apt", "apt-get", "brew", "yum", "dnf", "pacman", 
    "wget", "curl", "ssh", "scp", "rsync", "ftp", "sftp", "telnet",
    "passwd", "useradd", "userdel", "groupadd", "groupdel",
    "export", "env", "printenv"
]

FORBIDDEN_PATTERNS = [
    # Sensitive file patterns
    r'\.env$', r'\.pem$', r'\.key$', r'\.crt$', r'\.p12$', r'password', r'secret',
    r'credential', r'token', r'auth', r'\.ssh/', r'id_rsa', r'\.aws/', r'\.config/',
    
    # System file patterns
    r'/etc/', r'/var/', r'/proc/', r'/sys/', r'/dev/', r'/boot/', r'/root/',
    
    # Command patterns
    r'\s*>\s*/(?!tmp)', r'\s*>>\s*/(?!tmp)',  # Redirects to system dirs
    r'\|\s*(?:bash|sh|zsh|ksh|csh|tcsh)',      # Piping to shells
    r'`.*`', r'\$\(.*\)',                      # Command substitution
    r'&\s*$', r';\s*(?:sleep|wait)',           # Background execution
    
    # Web/network indicators
    r'http://', r'https://', r'ftp://', r'ssh://',
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'      # IP addresses
]