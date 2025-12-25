"""
Reality Fracture System - "Unsafe Menu" and reality glitch effects.
The menu isn't safe. Reality isn't stable. The fourth wall is cracking.

Fractures are rare, triggered events that break immersion deliberately:
- Save menu displays wrong timestamps
- Menu choices have in-world consequences
- Text corrupts, repeats, or references things that haven't happened

Per Canon & Constraints: Fractures never break saves; all changes are normal state effects.
"""

import random
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class FractureType(Enum):
    TIMESTAMP_CORRUPTION = "timestamp"
    TEXT_CORRUPTION = "text"
    MENU_INTRUSION = "menu"
    FOURTH_WALL = "fourth_wall"
    MEMORY_LEAK = "memory"
    DEJA_VU = "deja_vu"


class FractureSeverity(Enum):
    SUBTLE = 1      # Player might not notice
    NOTICEABLE = 2  # Something is wrong
    OBVIOUS = 3     # Reality is breaking
    SEVERE = 4      # The game is aware of you


@dataclass
class FractureEffect:
    """A single fracture effect that can be applied."""
    id: str
    type: FractureType
    severity: FractureSeverity
    description: str
    text_modification: Optional[Callable[[str], str]] = None
    menu_modification: Optional[dict] = None
    game_effects: List[dict] = field(default_factory=list)
    one_time: bool = False
    triggered: bool = False


@dataclass
class FractureEvent:
    """A recorded fracture occurrence."""
    effect_id: str
    timestamp: datetime
    trigger_source: str
    attention_level: int
    day: int


class FractureSystem:
    """
    Manages reality fractures and the "unsafe menu" mechanic.

    Fractures can trigger on:
    - Attention threshold exceeded
    - Specific scene flags
    - Random chance during storms
    - Certain menu interactions

    Fractures NEVER:
    - Corrupt actual save data
    - Make the game unwinnable
    - Break core mechanics

    Fractures ALWAYS:
    - Apply normal state effects (attention, time, flags)
    - Are recoverable
    - Serve the narrative of unreliable reality
    """

    def __init__(self, game_state=None):
        self.game_state = game_state
        self.fracture_effects: Dict[str, FractureEffect] = {}
        self.fracture_history: List[FractureEvent] = []
        self.active_fractures: List[str] = []

        # Trigger thresholds
        self.attention_threshold = 75
        self.storm_fracture_chance = 0.1
        self.base_fracture_chance = 0.02

        # State
        self.fractures_enabled = True
        self.current_day = 1
        self.current_attention = 0
        self.in_storm = False

        # Load default fracture effects
        self._load_default_effects()

    def _load_default_effects(self):
        """Load built-in fracture effects."""

        # === TIMESTAMP CORRUPTIONS ===
        self.register_effect(FractureEffect(
            id="fracture_wrong_date",
            type=FractureType.TIMESTAMP_CORRUPTION,
            severity=FractureSeverity.SUBTLE,
            description="The date is wrong.",
            menu_modification={
                "save_date_override": "October 47th, 1995",
                "display_text": "Last saved: October 47th, 1995 at 3:47 AM"
            }
        ))

        self.register_effect(FractureEffect(
            id="fracture_negative_time",
            type=FractureType.TIMESTAMP_CORRUPTION,
            severity=FractureSeverity.NOTICEABLE,
            description="Time runs backwards.",
            menu_modification={
                "save_date_override": "[TIME ERROR: NEGATIVE VALUE]",
                "time_display": "-03:47:???"
            }
        ))

        self.register_effect(FractureEffect(
            id="fracture_future_save",
            type=FractureType.TIMESTAMP_CORRUPTION,
            severity=FractureSeverity.OBVIOUS,
            description="A save from the future.",
            menu_modification={
                "save_date_override": "Day 67 of 67 - FINAL",
                "additional_saves": [
                    {"name": "Autosave (You)", "date": "After", "corrupted": True}
                ]
            }
        ))

        # === TEXT CORRUPTIONS ===
        self.register_effect(FractureEffect(
            id="fracture_repeated_phrase",
            type=FractureType.TEXT_CORRUPTION,
            severity=FractureSeverity.SUBTLE,
            description="A phrase echoes.",
            text_modification=self._repeat_phrase
        ))

        self.register_effect(FractureEffect(
            id="fracture_redacted_words",
            type=FractureType.TEXT_CORRUPTION,
            severity=FractureSeverity.NOTICEABLE,
            description="Words are censored.",
            text_modification=self._redact_words
        ))

        self.register_effect(FractureEffect(
            id="fracture_wrong_pronoun",
            type=FractureType.TEXT_CORRUPTION,
            severity=FractureSeverity.SUBTLE,
            description="Who is 'you'?",
            text_modification=self._wrong_pronoun
        ))

        # === MENU INTRUSIONS ===
        self.register_effect(FractureEffect(
            id="fracture_menu_choice",
            type=FractureType.MENU_INTRUSION,
            severity=FractureSeverity.OBVIOUS,
            description="A menu choice has consequences.",
            menu_modification={
                "inject_choice": {
                    "text": "Look behind you",
                    "effect": {"type": "modify_attention", "value": 10}
                }
            },
            game_effects=[{"type": "modify_attention", "value": 5}]
        ))

        self.register_effect(FractureEffect(
            id="fracture_save_warning",
            type=FractureType.MENU_INTRUSION,
            severity=FractureSeverity.NOTICEABLE,
            description="The save menu warns you.",
            menu_modification={
                "save_screen_text": "Are you sure you want to save? It already knows where you are.",
                "confirm_button_text": "I understand"
            }
        ))

        self.register_effect(FractureEffect(
            id="fracture_quit_refusal",
            type=FractureType.MENU_INTRUSION,
            severity=FractureSeverity.SEVERE,
            description="The game doesn't want you to leave.",
            menu_modification={
                "quit_text": "You can't leave. Not yet.",
                "quit_delay_seconds": 3,
                "alternative_text": "...fine. Go."
            },
            one_time=True
        ))

        # === FOURTH WALL BREAKS ===
        self.register_effect(FractureEffect(
            id="fracture_knows_player",
            type=FractureType.FOURTH_WALL,
            severity=FractureSeverity.OBVIOUS,
            description="It knows you're playing.",
            text_modification=lambda text: text + "\n\n[The investigator is aware they are being watched. Not by anyone in Kaltvik.]",
            game_effects=[{"type": "modify_attention", "value": 15}],
            one_time=True
        ))

        self.register_effect(FractureEffect(
            id="fracture_instruction",
            type=FractureType.FOURTH_WALL,
            severity=FractureSeverity.SEVERE,
            description="Instructions appear.",
            text_modification=lambda text: "[INSTRUCTION: Do not look at the aurora directly. Do not count the missing. Do not remember.]\n\n" + text,
            one_time=True
        ))

        # === MEMORY LEAKS ===
        self.register_effect(FractureEffect(
            id="fracture_wrong_memory",
            type=FractureType.MEMORY_LEAK,
            severity=FractureSeverity.SUBTLE,
            description="A memory that isn't yours.",
            text_modification=lambda text: text + "\n\n(You remember this happening differently. But you weren't there... were you?)"
        ))

        self.register_effect(FractureEffect(
            id="fracture_missing_entry",
            type=FractureType.MEMORY_LEAK,
            severity=FractureSeverity.NOTICEABLE,
            description="Something is missing.",
            menu_modification={
                "journal_modification": {
                    "missing_entries": [3, 7, 12],
                    "replacement_text": "[This page has been torn out. By you.]"
                }
            }
        ))

        # === DEJA VU ===
        self.register_effect(FractureEffect(
            id="fracture_deja_vu",
            type=FractureType.DEJA_VU,
            severity=FractureSeverity.SUBTLE,
            description="This has happened before.",
            text_modification=lambda text: text + "\n\n(This feels familiar. Too familiar.)"
        ))

        self.register_effect(FractureEffect(
            id="fracture_loop_hint",
            type=FractureType.DEJA_VU,
            severity=FractureSeverity.OBVIOUS,
            description="Time is looping.",
            text_modification=lambda text: "[Iteration: 347]\n\n" + text,
            one_time=True
        ))

    def register_effect(self, effect: FractureEffect):
        """Register a fracture effect."""
        self.fracture_effects[effect.id] = effect

    def update_state(self, attention: int = None, day: int = None, in_storm: bool = None):
        """Update system state for fracture calculations."""
        if attention is not None:
            self.current_attention = attention
        if day is not None:
            self.current_day = day
        if in_storm is not None:
            self.in_storm = in_storm

    def should_fracture(self, context: str = "general") -> bool:
        """Determine if a fracture should occur based on current state."""
        if not self.fractures_enabled:
            return False

        # High attention = high fracture chance
        if self.current_attention >= self.attention_threshold:
            if random.random() < 0.3:  # 30% chance at high attention
                return True

        # Storm increases chance
        if self.in_storm:
            if random.random() < self.storm_fracture_chance:
                return True

        # Late game increases chance
        day_modifier = self.current_day / 67.0  # 0 to 1 over the game
        adjusted_chance = self.base_fracture_chance * (1 + day_modifier)

        return random.random() < adjusted_chance

    def get_fracture_effect(self, context: str = "general",
                            preferred_type: FractureType = None) -> Optional[FractureEffect]:
        """Get a suitable fracture effect for the current context."""
        # Filter available effects
        available = [
            effect for effect in self.fracture_effects.values()
            if not (effect.one_time and effect.triggered)
        ]

        if not available:
            return None

        # Prefer certain types based on context
        if preferred_type:
            typed = [e for e in available if e.type == preferred_type]
            if typed:
                available = typed

        # Weight by severity and attention
        weights = []
        for effect in available:
            weight = 1.0

            # Higher attention = more severe fractures
            if self.current_attention >= 80:
                weight *= effect.severity.value
            elif self.current_attention >= 60:
                weight *= (4 - effect.severity.value)  # Prefer subtle
            else:
                weight *= (5 - effect.severity.value)  # Strongly prefer subtle

            weights.append(weight)

        # Weighted random selection
        total = sum(weights)
        if total == 0:
            return random.choice(available)

        r = random.random() * total
        cumulative = 0
        for effect, weight in zip(available, weights):
            cumulative += weight
            if r <= cumulative:
                return effect

        return available[-1]

    def trigger_fracture(self, effect: FractureEffect, source: str = "automatic") -> FractureEvent:
        """Trigger a specific fracture effect."""
        if effect.one_time:
            effect.triggered = True

        event = FractureEvent(
            effect_id=effect.id,
            timestamp=datetime.now(),
            trigger_source=source,
            attention_level=self.current_attention,
            day=self.current_day
        )

        self.fracture_history.append(event)
        self.active_fractures.append(effect.id)

        print(f"[FRACTURE] {effect.description} (Severity: {effect.severity.name})")

        return event

    def apply_text_fracture(self, text: str, effect: FractureEffect = None) -> Tuple[str, Optional[FractureEffect]]:
        """
        Apply a text fracture effect to narrative text.
        Returns (modified_text, effect_used) or (original_text, None).
        """
        if not self.should_fracture("text") and effect is None:
            return text, None

        if effect is None:
            effect = self.get_fracture_effect("text", FractureType.TEXT_CORRUPTION)

        if effect is None or effect.text_modification is None:
            return text, None

        try:
            modified = effect.text_modification(text)
            self.trigger_fracture(effect, "text_render")
            return modified, effect
        except Exception as e:
            print(f"[FRACTURE] Error applying text fracture: {e}")
            return text, None

    def get_menu_modifications(self, menu_type: str = "main") -> dict:
        """Get any active menu modifications."""
        if not self.should_fracture("menu"):
            return {}

        effect = self.get_fracture_effect("menu", FractureType.MENU_INTRUSION)
        if effect is None or effect.menu_modification is None:
            # Try timestamp corruption for save menu
            if menu_type == "save":
                effect = self.get_fracture_effect("save", FractureType.TIMESTAMP_CORRUPTION)
                if effect and effect.menu_modification:
                    self.trigger_fracture(effect, f"menu_{menu_type}")
                    return effect.menu_modification
            return {}

        self.trigger_fracture(effect, f"menu_{menu_type}")
        return effect.menu_modification

    def get_game_effects(self, effect: FractureEffect) -> List[dict]:
        """Get game state effects from a fracture."""
        return effect.game_effects

    # === TEXT MODIFICATION FUNCTIONS ===

    def _repeat_phrase(self, text: str) -> str:
        """Repeat a phrase in the text."""
        sentences = text.split(". ")
        if len(sentences) > 2:
            idx = random.randint(0, min(2, len(sentences) - 1))
            sentences.insert(idx + 1, sentences[idx])
        return ". ".join(sentences)

    def _redact_words(self, text: str) -> str:
        """Redact random words."""
        words = text.split()
        if len(words) < 10:
            return text

        # Redact 1-3 words
        num_redactions = random.randint(1, 3)
        indices = random.sample(range(len(words)), min(num_redactions, len(words)))

        for idx in indices:
            word = words[idx]
            # Keep first letter, redact rest
            if len(word) > 2:
                words[idx] = word[0] + "█" * (len(word) - 1)

        return " ".join(words)

    def _wrong_pronoun(self, text: str) -> str:
        """Subtly use wrong pronouns."""
        replacements = [
            ("you ", "they "),
            ("You ", "They "),
            ("your ", "their "),
            ("Your ", "Their "),
        ]

        # Only replace once, subtly
        replacement = random.choice(replacements)
        count = text.count(replacement[0])
        if count > 0:
            idx = random.randint(1, count)
            parts = text.split(replacement[0])
            if len(parts) > idx:
                return replacement[0].join(parts[:idx]) + replacement[1] + replacement[0].join(parts[idx:])

        return text

    def clear_active_fractures(self):
        """Clear active fractures (e.g., on scene change)."""
        self.active_fractures.clear()

    def to_dict(self) -> dict:
        """Serialize fracture state for saving."""
        return {
            "history": [
                {
                    "effect_id": e.effect_id,
                    "trigger_source": e.trigger_source,
                    "attention_level": e.attention_level,
                    "day": e.day
                }
                for e in self.fracture_history
            ],
            "triggered_one_time": [
                eid for eid, e in self.fracture_effects.items()
                if e.one_time and e.triggered
            ]
        }

    def restore_state(self, state: dict):
        """Restore fracture state from saved data."""
        for eid in state.get("triggered_one_time", []):
            if eid in self.fracture_effects:
                self.fracture_effects[eid].triggered = True


class UnsafeMenu:
    """
    The "Unsafe Menu" - a menu system that can be compromised by fractures.
    Wraps standard menu operations with fracture awareness.
    """

    def __init__(self, fracture_system: FractureSystem):
        self.fracture_system = fracture_system
        self.menu_stack: List[str] = []

    def open_menu(self, menu_type: str) -> dict:
        """
        Open a menu, potentially with fracture modifications.
        Returns dict with menu state and any modifications.
        """
        self.menu_stack.append(menu_type)

        result = {
            "menu_type": menu_type,
            "modifications": {},
            "fractured": False
        }

        # Check for menu fractures
        mods = self.fracture_system.get_menu_modifications(menu_type)
        if mods:
            result["modifications"] = mods
            result["fractured"] = True

        return result

    def close_menu(self) -> Optional[str]:
        """Close the current menu."""
        if self.menu_stack:
            return self.menu_stack.pop()
        return None

    def get_save_display(self, saves: List[dict]) -> List[dict]:
        """
        Get save entries with potential fracture modifications.
        """
        # Get any timestamp modifications
        mods = self.fracture_system.get_menu_modifications("save")

        if not mods:
            return saves

        modified_saves = []
        for save in saves:
            mod_save = save.copy()

            # Apply timestamp override
            if "save_date_override" in mods:
                mod_save["display_date"] = mods["save_date_override"]

            modified_saves.append(mod_save)

        # Add any injected saves
        if "additional_saves" in mods:
            for ghost_save in mods["additional_saves"]:
                modified_saves.append({
                    "id": f"ghost_{len(modified_saves)}",
                    "name": ghost_save.get("name", "???"),
                    "date": ghost_save.get("date", "Unknown"),
                    "is_ghost": True,
                    "corrupted": ghost_save.get("corrupted", False)
                })

        return modified_saves

    def handle_quit(self) -> Tuple[bool, Optional[str]]:
        """
        Handle quit request, potentially with fracture interference.
        Returns (allow_quit, message).
        """
        mods = self.fracture_system.get_menu_modifications("quit")

        if not mods:
            return True, None

        if "quit_text" in mods:
            return True, mods["quit_text"]

        return True, None


if __name__ == "__main__":
    # Test fracture system
    system = FractureSystem()
    system.update_state(attention=80, day=30, in_storm=True)

    print("=== FRACTURE SYSTEM TEST ===\n")

    # Test text fracture
    sample_text = "You enter the hotel lobby. The clock on the wall shows 3:47. The air smells of old coffee and something metallic."

    print("Original text:")
    print(sample_text)
    print()

    # Force some fractures for testing
    for i in range(3):
        modified, effect = system.apply_text_fracture(sample_text)
        if effect:
            print(f"\nFracture {i+1}: {effect.description}")
            print(modified)

    print("\n" + "=" * 40 + "\n")

    # Test menu modifications
    menu = UnsafeMenu(system)

    print("Opening save menu:")
    result = menu.open_menu("save")
    print(f"Fractured: {result['fractured']}")
    if result['modifications']:
        print(f"Modifications: {result['modifications']}")

    print("\n" + "=" * 40 + "\n")

    # Show fracture history
    print("Fracture history:")
    for event in system.fracture_history:
        effect = system.fracture_effects.get(event.effect_id)
        print(f"  - Day {event.day}: {effect.description if effect else event.effect_id}")
