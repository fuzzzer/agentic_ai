import os

DEFAULT_USER_ROLE = "basic"
ADMIN_USER_ROLE = "admin"
DOCKER_ENV_IDENTIFIER = "docker"

## Docker Commands
DOCKER_PERMITTED_OS_DIRECTORIES =   [
    "/"  # Full container filesystem access; ensure sensitive host directories are not mounted.
]

DOCKER_ALLOWED_OS_COMMANDS = [
    "ls", "pwd", "mkdir", "rmdir", "touch", "cat", "cp", "mv", "echo", "grep", "cd",
    "bash", "sh", "sed", "awk", "find", "sort", "uniq", "head", "tail",
    "rm", "chmod", "chown",
    "kill", "pkill", "dd", "mkfs", "fdisk",
    "apt", "apt-get", "yum", "dnf", "pacman",
    "wget", "curl", "ssh", "scp", "rsync", "ftp", "sftp", "telnet",
    "python", "pip", 
    # "git", "node", "npm"
]

DOCKER_FORBIDDEN_COMMANDS = [
    # Dangerous or privilege-escalating commands
    "sudo", "su",
    "reboot", "shutdown", "halt", "poweroff",
    "init",                                    
    "mount", "umount",                         
    "iptables", "systemctl", "service"        
]

DOCKER_FORBIDDEN_PATTERNS = [
    # Block dangerous piping to shells.
    r'\|\s*(?:bash|sh|zsh|ksh|csh|tcsh)',
    
    # Block command substitution constructs (e.g. $(...)) or backticks.
    r'`.*`', r'\$\(.*\)',
    
    # Block background execution with certain commands to avoid runaway processes.
    r'&\s*$', r';\s*(?:sleep|wait)',
    
    # Optional: Block external web/network requests if desired.
    # r'http://', r'https://', r'ftp://', r'ssh://',
    # r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
]



## NON Docker Commands
PERMITTED_OS_DIRECTORIES = [
    ## your path, should be explicitely set to double check and assure that user knows what she/he's doing :D
    '/Users/fuzzzer/programming/AI_tools/agentic_ai/playground'
]

ALLOWED_OS_COMMANDS = [
    "ls", "pwd", "mkdir", "rmdir", "touch", "cat", "cp", "mv", "echo", "grep", "cd",
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
    "export", "env", "printenv", "pip"
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