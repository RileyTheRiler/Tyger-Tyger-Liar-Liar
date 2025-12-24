from typing import List, Dict, Callable
from tyger_game.ui.interface import print_text, get_input, Colors

class DialogueManager:
    """
    Manages dialogue interactions.
    Currently a stub for Phase 1, to be expanded with JSON loaded dialogues.
    """
    def __init__(self):
        self.active = False
    
    def start_dialogue(self, dialogue_node: Dict):
        self.active = True
        self._run_node(dialogue_node)

    def _run_node(self, node: Dict):
        while self.active:
            print_text(f"{node.get('speaker', 'Unknown')}: \"{node.get('text', '...')}\"", Colors.CYAN)
            
            choices = node.get('choices', [])
            if not choices:
                self.active = False
                return

            print("\n")
            for idx, choice in enumerate(choices):
                print(f"{idx + 1}. {choice['text']}")
            
            selection = get_input("\nChoose > ")
            
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(choices):
                    chosen = choices[idx]
                    # Logic to move to next node would go here
                    print_text(f"> You chose: {chosen['text']}")
                    self.active = False # End for now
                else:
                    print_text("Invalid choice.", Colors.FAIL)
            except ValueError:
                print_text("Please enter a number.", Colors.FAIL)
