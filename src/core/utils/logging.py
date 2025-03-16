import logging
import sys
from colorama import init, Fore, Style

# Initialize colorama (ensures compatibility inside Docker)
init(autoreset=True)

# Define ANSI color styles
COLOR_MAP = {
    "DEBUG": Fore.YELLOW,
    "INFO": Fore.GREEN,
    "WARNING": Fore.RED,
    "ERROR": Fore.MAGENTA,
    "CRITICAL": Fore.RED + Style.BRIGHT,
}

# Custom log formatter with colors
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_color = COLOR_MAP.get(record.levelname, "")
        return f"{Fore.CYAN}{record.asctime}{Style.RESET_ALL} - {log_color}{record.levelname}{Style.RESET_ALL} - {record.message}"

# Setup logger inside main
def setup_logger():
    logger = logging.getLogger("MyLogger")
    logger.setLevel(logging.DEBUG)  # Set desired log level

    formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    return logger