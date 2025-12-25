
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from interface import print_boxed_title, print_separator, print_numbered_list, format_skill_result, Colors

def test_colors():
    print(f"{Colors.RED}Testing Red{Colors.RESET}")
    print(f"{Colors.GREEN}Testing Green{Colors.RESET}")
    print(f"{Colors.CYAN}Testing Cyan{Colors.RESET}")
    print(f"{Colors.YELLOW}Testing Yellow{Colors.RESET}")

def test_interface_functions():
    print("Testing print_boxed_title:")
    print_boxed_title("TEST TITLE")

    print("\nTesting print_separator:")
    print_separator()

    print("\nTesting print_numbered_list:")
    items = ["Option A", "Option B"]
    print_numbered_list("Test List", items)

    print("\nTesting print_numbered_list (dict):")
    dict_items = [
        {"text": "Available Option", "enabled": True},
        {"text": "Locked Option", "enabled": False, "reason": "Low Sanity"}
    ]
    print_numbered_list("Complex List", dict_items)

    print("\nTesting format_skill_result:")
    result_success = {
        "skill": "Logic",
        "roll": 7,
        "modifier": 1,
        "total": 8,
        "difficulty": 6,
        "success": True,
        "description": "You deduced the truth."
    }
    format_skill_result(result_success)

    result_fail = {
        "skill": "Force",
        "roll": 3,
        "modifier": 0,
        "total": 3,
        "difficulty": 6,
        "success": False
    }
    format_skill_result(result_fail)

if __name__ == "__main__":
    test_colors()
    test_interface_functions()
    print("\nInterface verification complete.")
