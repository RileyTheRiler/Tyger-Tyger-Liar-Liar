"""
Text Composer - The "Bad Blood" Narrative Engine.
Composes scene text from: base + lens overlay + skill-based inserts + fracture effects.
Allows writing one scene with multiple interpretations without tripling workload.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class InsertPosition(Enum):
    BEFORE_CHOICES = "BEFORE_CHOICES"
    AFTER_BASE = "AFTER_BASE"
    AFTER_LENS = "AFTER_LENS"
    MID_PARAGRAPH = "MID_PARAGRAPH"


class Archetype(Enum):
    BELIEVER = "believer"
    SKEPTIC = "skeptic"
    HAUNTED = "haunted"
    NEUTRAL = "neutral"


@dataclass
class TextInsert:
    """A conditional text insert that appears based on player state."""
    id: str
    text: str
    position: InsertPosition
    condition: dict = field(default_factory=dict)


@dataclass
class ComposedText:
    """The result of text composition."""
    full_text: str
    base_used: bool
    lens_used: Optional[str]
    inserts_applied: List[str]
    fracture_applied: bool
    debug_info: dict = field(default_factory=dict)


# Predefined micro-overlays for when full lens text isn't provided
MICRO_OVERLAYS = {
    Archetype.BELIEVER: {
        "adjectives": ["otherworldly", "unnatural", "significant", "portentous"],
        "verbs": ["seems to", "appears to", "feels like it"],
        "atmosphere": "The air feels charged with something unseen."
    },
    Archetype.SKEPTIC: {
        "adjectives": ["mundane", "explainable", "coincidental", "ordinary"],
        "verbs": ["probably", "likely", "must be"],
        "atmosphere": "There's a rational explanation. There always is."
    },
    Archetype.HAUNTED: {
        "adjectives": ["familiar", "echoing", "memory-touched", "haunting"],
        "verbs": ["reminds you of", "echoes", "brings back"],
        "atmosphere": "You've seen this before. Haven't you?"
    }
}


class TextComposer:
    """
    Composes narrative text with lens overlays and conditional inserts.

    Text layering order:
    1. Base layer: Objective anchor text (short, minimal)
    2. Lens layer: Archetype overlay (Believer/Skeptic/Haunted)
    3. Perception layer: Optional inserts unlocked by skill thresholds
    4. Fracture layer: Rare reality glitches (triggered by attention/flags)
    """

    def __init__(self, skill_system=None, board=None, game_state=None):
        self.skill_system = skill_system
        self.board = board
        self.game_state = game_state
        self.debug_mode = False
        self.fracture_chance = 0.0  # Base chance for random fractures

    def compose(self, text_data: dict, archetype: Archetype = Archetype.NEUTRAL,
                player_state: dict = None) -> ComposedText:
        """
        Compose final text from text data.

        Args:
            text_data: Dict containing 'base', optional 'lens', and optional 'inserts'
            archetype: Current player archetype
            player_state: Dict with skills, flags, theories, equipment, etc.

        Returns:
            ComposedText with composed narrative
        """
        player_state = player_state or {}
        debug_info = {"layers": []}

        # === LAYER 1: BASE TEXT ===
        base_text = text_data.get("base", "")
        if not base_text:
            return ComposedText(
                full_text="[No text defined]",
                base_used=False,
                lens_used=None,
                inserts_applied=[],
                fracture_applied=False
            )

        result_parts = []
        result_parts.append(base_text)
        debug_info["layers"].append("base")

        # === LAYER 2: LENS OVERLAY ===
        lens_text = None
        lens_data = text_data.get("lens", {})

        if archetype != Archetype.NEUTRAL and archetype.value in lens_data:
            lens_text = lens_data[archetype.value]
            result_parts.append("\n\n" + lens_text)
            debug_info["layers"].append(f"lens:{archetype.value}")
        elif archetype != Archetype.NEUTRAL:
            # Apply micro-overlay if no full lens text
            micro = self._apply_micro_overlay(base_text, archetype)
            if micro != base_text:
                result_parts.append("\n\n" + micro)
                debug_info["layers"].append(f"micro_overlay:{archetype.value}")

        # === LAYER 3: CONDITIONAL INSERTS ===
        inserts_applied = []
        inserts_data = text_data.get("inserts", [])

        # Collect inserts by position
        after_base_inserts = []
        after_lens_inserts = []
        before_choices_inserts = []

        for insert_data in inserts_data:
            if self._check_insert_condition(insert_data.get("condition", {}), player_state):
                insert_text = insert_data.get("text", "")
                position_str = insert_data.get("insert_at", "AFTER_LENS")

                try:
                    position = InsertPosition(position_str)
                except ValueError:
                    position = InsertPosition.AFTER_LENS

                insert_id = insert_data.get("id", f"insert_{len(inserts_applied)}")
                inserts_applied.append(insert_id)
                debug_info["layers"].append(f"insert:{insert_id}")

                if position == InsertPosition.AFTER_BASE:
                    after_base_inserts.append(insert_text)
                elif position == InsertPosition.AFTER_LENS:
                    after_lens_inserts.append(insert_text)
                elif position == InsertPosition.BEFORE_CHOICES:
                    before_choices_inserts.append(insert_text)

        # Build final text
        final_parts = [base_text]

        # After base inserts
        for insert in after_base_inserts:
            final_parts.append("\n" + insert)

        # Lens text
        if lens_text:
            final_parts.append("\n\n" + lens_text)
        elif archetype != Archetype.NEUTRAL and "micro_overlay" in str(debug_info["layers"]):
            micro = self._apply_micro_overlay(base_text, archetype)
            final_parts.append("\n\n" + MICRO_OVERLAYS[archetype]["atmosphere"])

        # After lens inserts
        for insert in after_lens_inserts:
            final_parts.append("\n" + insert)

        # Before choices inserts
        for insert in before_choices_inserts:
            final_parts.append("\n\n" + insert)

        full_text = "".join(final_parts)

        # === LAYER 4: FRACTURE EFFECTS ===
        fracture_applied = False
        if self._should_apply_fracture(player_state):
            full_text = self._apply_fracture_effect(full_text, player_state)
            fracture_applied = True
            debug_info["layers"].append("fracture")

        return ComposedText(
            full_text=full_text.strip(),
            base_used=True,
            lens_used=archetype.value if lens_text else None,
            inserts_applied=inserts_applied,
            fracture_applied=fracture_applied,
            debug_info=debug_info if self.debug_mode else {}
        )

    def _apply_micro_overlay(self, text: str, archetype: Archetype) -> str:
        """
        Apply subtle lens adjectives when full lens text isn't available.
        This ensures archetype always affects perception without requiring
        full alternate text for every scene.
        """
        if archetype not in MICRO_OVERLAYS:
            return text

        overlay = MICRO_OVERLAYS[archetype]
        return overlay["atmosphere"]

    def _check_insert_condition(self, condition: dict, player_state: dict) -> bool:
        """Check if an insert's condition is met."""
        if not condition:
            return True

        # Skill threshold check: skill_gte
        skill_gte = condition.get("skill_gte", {})
        for skill_name, threshold in skill_gte.items():
            player_skill = self._get_skill_value(skill_name, player_state)
            if player_skill < threshold:
                return False

        # Flag check
        flag_set = condition.get("flag_set")
        if flag_set:
            flags = player_state.get("flags", {})
            if isinstance(flags, set):
                if flag_set not in flags:
                    return False
            elif isinstance(flags, dict):
                if not flags.get(flag_set, False):
                    return False

        # Theory active check
        theory_active = condition.get("theory_active")
        if theory_active:
            active_theories = player_state.get("active_theories", [])
            if theory_active not in active_theories:
                return False

        # Trust threshold check
        trust_gte = condition.get("trust_gte", {})
        for npc_id, threshold in trust_gte.items():
            trust_levels = player_state.get("trust", {})
            if trust_levels.get(npc_id, 0) < threshold:
                return False

        # Attention threshold check
        attention_gte = condition.get("attention_gte")
        if attention_gte is not None:
            attention = player_state.get("attention", 0)
            if attention < attention_gte:
                return False

        # Equipment check
        equipment = condition.get("equipment")
        if equipment:
            inventory = player_state.get("inventory", [])
            if equipment not in inventory:
                return False

        return True

    def _get_skill_value(self, skill_name: str, player_state: dict) -> int:
        """Get a skill value from player state or skill system."""
        # Try player state first
        skills = player_state.get("skills", {})
        if skill_name in skills:
            return skills[skill_name]

        # Try skill system if available
        if self.skill_system:
            skill = self.skill_system.get_skill(skill_name)
            if skill:
                return skill.effective_level

        return 0

    def _should_apply_fracture(self, player_state: dict) -> bool:
        """
        Determine if a reality fracture should occur.
        Fractures are rare and triggered by attention/flags/storms.
        """
        # Check explicit fracture flag
        flags = player_state.get("flags", {})
        if isinstance(flags, set):
            if "trigger_fracture" in flags:
                return True
        elif isinstance(flags, dict):
            if flags.get("trigger_fracture", False):
                return True

        # Check attention threshold
        attention = player_state.get("attention", 0)
        if attention >= 75:
            import random
            return random.random() < 0.15  # 15% chance at high attention

        # Base random chance (very low)
        if self.fracture_chance > 0:
            import random
            return random.random() < self.fracture_chance

        return False

    def _apply_fracture_effect(self, text: str, player_state: dict) -> str:
        """
        Apply a reality fracture effect to the text.
        These are subtle wrongnesses that break the fourth wall or reality.
        """
        import random

        fracture_types = [
            self._fracture_timestamp,
            self._fracture_repetition,
            self._fracture_wrong_name,
            self._fracture_extra_paragraph
        ]

        # Choose a random fracture type
        fracture = random.choice(fracture_types)
        return fracture(text, player_state)

    def _fracture_timestamp(self, text: str, player_state: dict) -> str:
        """Add a wrong timestamp notation."""
        wrong_dates = [
            "[03:47 AM - Day ???]",
            "[TIME ERROR: NEGATIVE VALUE]",
            "[Entry 347 of 346]",
            "[October 47th, 1995]"
        ]
        import random
        return random.choice(wrong_dates) + "\n\n" + text

    def _fracture_repetition(self, text: str, player_state: dict) -> str:
        """Repeat a phrase eerily."""
        sentences = text.split(". ")
        if len(sentences) > 2:
            import random
            idx = random.randint(0, len(sentences) - 2)
            sentences.insert(idx + 1, sentences[idx])
            return ". ".join(sentences)
        return text

    def _fracture_wrong_name(self, text: str, player_state: dict) -> str:
        """Briefly use the wrong name."""
        player_name = player_state.get("player_name", "you")
        wrong_names = ["[REDACTED]", "the other one", "█████", "yourself"]
        import random
        # Simple replacement - in real implementation, would be more sophisticated
        return text + f"\n\n[{random.choice(wrong_names)} continues...]"

    def _fracture_extra_paragraph(self, text: str, player_state: dict) -> str:
        """Add an impossible paragraph."""
        extras = [
            "\n\n(You remember writing this. But you haven't yet.)",
            "\n\n[This section appears to be from a different document entirely.]",
            "\n\nYou skip ahead. The page is blank. You go back. The words are different now.",
            "\n\n[Note: The investigator is reminded that they are not the first. They are not the last.]"
        ]
        import random
        return text + random.choice(extras)


class ClueTextComposer:
    """Specialized composer for clue descriptions."""

    def __init__(self, text_composer: TextComposer):
        self.composer = text_composer

    def compose_clue(self, clue_data: dict, archetype: Archetype,
                     player_state: dict = None) -> str:
        """Compose clue text with lens interpretation."""
        text_data = clue_data.get("text", {})
        if isinstance(text_data, str):
            text_data = {"base": text_data}

        result = self.composer.compose(text_data, archetype, player_state)
        return result.full_text


class DialogueTextComposer:
    """Specialized composer for dialogue with speaker and lens variants."""

    def __init__(self, text_composer: TextComposer):
        self.composer = text_composer

    def compose_line(self, line_data: dict, archetype: Archetype,
                     player_state: dict = None) -> Tuple[str, str]:
        """
        Compose a dialogue line.
        Returns (speaker, composed_text).
        """
        speaker = line_data.get("speaker", "???")

        # Compose the dialogue text
        text_data = line_data.get("text", {})
        if isinstance(text_data, str):
            text_data = {"base": text_data}

        result = self.composer.compose(text_data, archetype, player_state)

        # Apply speaker-specific lens (NPCs might speak differently based on player's lens)
        if archetype == Archetype.HAUNTED:
            # In haunted lens, speakers might seem more suspicious
            if "lens" not in line_data.get("text", {}):
                speaker = f"{speaker} (familiar)"

        return speaker, result.full_text


# Debug mode helpers
def enable_debug_mode(composer: TextComposer):
    """Enable debug mode on a composer."""
    composer.debug_mode = True


def print_composition_debug(result: ComposedText):
    """Print debug info for a composition."""
    print("=== COMPOSITION DEBUG ===")
    print(f"Base used: {result.base_used}")
    print(f"Lens used: {result.lens_used}")
    print(f"Inserts applied: {result.inserts_applied}")
    print(f"Fracture applied: {result.fracture_applied}")
    if result.debug_info:
        print(f"Layers: {result.debug_info.get('layers', [])}")
    print("=========================")


if __name__ == "__main__":
    # Test the text composer
    composer = TextComposer()
    enable_debug_mode(composer)

    test_scene = {
        "base": "The hotel lobby is empty. A clock ticks somewhere. The air smells of old coffee and something else—something metallic.",
        "lens": {
            "believer": "The shadows in the corners seem to shift when you're not looking directly at them. The clock's rhythm is wrong, somehow. Counting down, not up.",
            "skeptic": "Standard small-town hotel. The metallic smell is probably from the old radiators. Nothing here that can't be explained.",
            "haunted": "You've been in this lobby before. The furniture was different then. Or was it? The clock's ticking sounds like a heartbeat. Whose?"
        },
        "inserts": [
            {
                "id": "forensics_smell",
                "condition": {"skill_gte": {"Forensics": 3}},
                "text": "That metallic smell—it's blood. Old blood, mostly cleaned, but not well enough.",
                "insert_at": "AFTER_LENS"
            },
            {
                "id": "perception_figure",
                "condition": {"skill_gte": {"Perception": 4}},
                "text": "There's a figure in the mirror behind the desk. When you turn to look, no one is there.",
                "insert_at": "BEFORE_CHOICES"
            }
        ]
    }

    print("=== BELIEVER ===")
    result = composer.compose(test_scene, Archetype.BELIEVER, {"skills": {"Forensics": 4, "Perception": 2}})
    print(result.full_text)
    print_composition_debug(result)

    print("\n=== SKEPTIC ===")
    result = composer.compose(test_scene, Archetype.SKEPTIC, {"skills": {"Forensics": 1, "Perception": 5}})
    print(result.full_text)
    print_composition_debug(result)

    print("\n=== HAUNTED ===")
    result = composer.compose(test_scene, Archetype.HAUNTED, {"skills": {"Forensics": 4, "Perception": 5}})
    print(result.full_text)
    print_composition_debug(result)
