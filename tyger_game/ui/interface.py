import os
import textwrap
import shutil
from tyger_game.utils.constants import Colors

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_text(text: str, color: str = None, speed: float = 0.0):
    """
    Prints text to the console, wrapping it to the window width.
    """
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
