from typing import Any
from text_composer import TextComposer

class FractureManager:
    def __init__(self, state, text_composer: TextComposer):
        self.state = state
        self.composer = text_composer

    def get_menu_text(self, original_text: str) -> str:
        """
        Returns menu text, potentially distorted by a reality fracture.
        """
        if self.composer._should_apply_fracture(self.state):
            # Apply a random fracture effect to the menu text
            return self.composer._apply_fracture_effect(original_text, self.state)
        return original_text

    def trigger_unsafe_moment(self) -> str:
        """Force an immediate 'unsafe' message."""
        return self.composer._fracture_timestamp("SYSTEM MENU", self.state)
