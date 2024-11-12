import sys

from datetime import datetime

def msg(type: str, message: str) -> int:
    """
    Print a message with a timestamp and a message type
    
    :param type: the type of the message (info, debug, warning, error), ``str``
    :param message: the message to print, ``str``
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if type == "info":
        print(f"[{timestamp}] [INFO] {message}")
    elif type == "debug":
        print(f"[{timestamp}] [DEBUG] {message}")
    elif type == "warning":
        print(f"[{timestamp}] [WARNING] {message}")
    elif type == "error":
        print(f"[{timestamp}] [ERROR] {message}")
        sys.exit(255)
    else:
        print(f"[{timestamp}] [UNKNOWN] {message}")
        sys.exit(255)