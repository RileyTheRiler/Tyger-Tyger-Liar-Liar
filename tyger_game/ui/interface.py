import os
import textwrap
import shutil
from tyger_game.utils.constants import Colors

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

# IO Handler
output_callback = print

def set_output_handler(callback):
    global output_callback
    output_callback = callback

def print_text(text: str, color: str = None, speed: float = 0.0):
    """
    Prints text to the console or registered handler, wrapping it.
    """
    # If we are using a custom handler (not print), we might just send the raw text
    # But for now let's keep the wrapping logic for consistency, or maybe pass raw text?
    # Let's pass the processed lines to the handler.
    
    if output_callback != print:
         # For API, we often want the full text blob, possibly with color metadata
         # But the simplest refactor is to just send the string.
         # Let's send the full text to the callback if it's not print.
         output_callback(text, color)
         return

    width = shutil.get_terminal_size().columns
    width = min(width, 100) # Cap width for readability
    
    wrapped_lines = textwrap.wrap(text, width=width)
    
    prefix = color if color else ""
    suffix = Colors.ENDC if color else ""
    
    for line in wrapped_lines:
        print(f"{prefix}{line}{suffix}")

def print_header(text: str):
    print_text(text, color=Colors.HEADER)
    print("-" * min(shutil.get_terminal_size().columns, 100))

def get_input(prompt_text: str = "> ") -> str:
    """Gets input from the user."""
    return input(prompt_text).strip()

def print_separator():
    print("\n" + "-" * 40 + "\n")
