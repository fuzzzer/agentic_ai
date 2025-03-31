import os
import builtins


def block_system_commands():
    # Disabling system-level commands
    os.remove = None
    os.rmdir = None
    os.unlink = None
    os.rename = None

    # Disabling dangerous built-in functions
    builtins.exec = None
    builtins.eval = None
