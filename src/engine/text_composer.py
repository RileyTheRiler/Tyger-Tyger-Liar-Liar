"""
Text Composer - The "Bad Blood" Narrative Engine.
Composes scene text from: base + lens overlay + skill-based inserts + fracture effects.
Allows writing one scene with multiple interpretations without tripling workload.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Import Colors for theory commentary formatting
try:
    from ui.interface import Colors
except ImportError:
    # Fallback if running standalone
    class Colors:
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        RESET = "\033[0m"


class InsertPosition(Enum):
    BEFORE_CHOICES = "BEFORE_CHOICES"
    AFTER_BASE = "AFTER_BASE"
    AFTER_LENS = "AFTER_LENS"
    MID_PARAGRAPH = "MID_PARAGRAPH"
    AFTER_PARAGRAPH = "AFTER_PARAGRAPH" # Usage: AFTER_PARAGRAPH:n


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

    def __init__(self, skill_system=None, board=None, game_state=None, lens_system=None):
        self.skill_system = skill_system
        self.board = board
        self.game_state = game_state
        self.lens_system = lens_system
        self.debug_mode = False
        self.developer_commentary = False
        self.fracture_chance = 0.0  # Base chance for random fractures
    
    def calculate_dominant_lens(self, player_state: dict = None) -> Archetype:
        """
        Calculate the dominant lens based on player's skills and active theories.
        If lens_system is available, delegates to it.
        """
        if self.lens_system:
            lens_str = self.lens_system.calculate_lens()
            try:
                return Archetype(lens_str)
            except ValueError:
                return Archetype.NEUTRAL

        if not self.skill_system or player_state is None:
            return Archetype.NEUTRAL
        
        # Fallback logic if lens_system is not provided
        # Calculate dominant attribute: Intuition vs Reason
        intuition_skills = ["Paranormal Sensitivity", "Instinct", "Subconscious", "Pattern Recognition"]
        reason_skills = ["Logic", "Skepticism", "Forensics", "Research"]
        
        intuition_total = sum(
            self.skill_system.get_skill(s).effective_level 
            for s in intuition_skills 
            if self.skill_system.get_skill(s)
        )
        reason_total = sum(
            self.skill_system.get_skill(s).effective_level 
            for s in reason_skills 
            if self.skill_system.get_skill(s)
        )
        
        # Check active theories for lens override
        if self.board:
            active_theories = [t.id for t in self.board.theories.values() if t.status == "active"]
            
            # Believer theories
            believer_theories = ["The Truth Is Out There", "The Nightmares Mean Something", "They're Watching Me"]
            # Skeptic theories
            skeptic_theories = ["Rational Explanation", "Mass Hysteria", "Government Coverup"]
            # Haunted theories
            haunted_theories = ["I've Been Here Before", "The Entity Knows Me"]
            
            believer_count = sum(1 for t in active_theories if t in believer_theories)
            skeptic_count = sum(1 for t in active_theories if t in skeptic_theories)
            haunted_count = sum(1 for t in active_theories if t in haunted_theories)
            
            # Theory override (theories are stronger than skills)
            if haunted_count > 0:
                return Archetype.HAUNTED
            if believer_count > skeptic_count:
                return Archetype.BELIEVER
            if skeptic_count > believer_count:
                return Archetype.SKEPTIC
        
        # Skill-based determination
        if intuition_total > reason_total + 3:
            return Archetype.BELIEVER
        elif reason_total > intuition_total + 3:
            return Archetype.SKEPTIC
        else:
            return Archetype.NEUTRAL

    def compose(self, text_data: dict, archetype: Archetype = Archetype.NEUTRAL,
                player_state: dict = None, thermal_mode: bool = False) -> ComposedText:
        """
        Compose final text from text data.

        Args:
            text_data: Dict containing 'base', optional 'lens', 'thermal', and optional 'inserts'
            archetype: Current player archetype
            player_state: Dict with skills, flags, theories, equipment, etc.
            thermal_mode: Whether thermal vision is active (overrides base text often)

        Returns:
            ComposedText with composed narrative
        """
        player_state = player_state or {}
        debug_info = {"layers": []}

        if "text" in text_data and isinstance(text_data["text"], dict):
            # If we were passed the whole scene dict, dig into the 'text' key
            scene_id = text_data.get("id", "unknown")
            text_data = text_data["text"]
            
        # === LAYER 1: BASE TEXT vs THERMAL ===
        base_text = text_data.get("base", "")
        thermal_text = text_data.get("thermal", "")
        
        # Thermal Logic: If active and available, it usually replaces or heavily modifies base
        if thermal_mode and thermal_text:
            text_to_use = thermal_text
            debug_info["layers"].append("thermal_base")
        else:
            text_to_use = base_text
            debug_info["layers"].append("base")

        if not text_to_use:
             return ComposedText(
                full_text=f"[No text defined for {text_data.get('id', 'scene')}]",
                base_used=False,
                lens_used=None,
                inserts_applied=[],
                fracture_applied=False
            )

        result_parts = []
        result_parts.append(text_to_use)

        # === LAYER 2: LENS OVERLAY (RESOLVED VIA LENS SYSTEM IF AVAILABLE) ===
        lens_text = None
        lens_data = text_data.get("lens", {})

        if lens_data and self.lens_system:
            # Use the new resolver
            stress = 0
            if self.game_state:
                stress = 100 - self.game_state.sanity
            elif player_state:
                stress = 100 - player_state.get("sanity", 100)

            lens_text = self.lens_system.resolve_text(archetype.value, stress, lens_data)
            if lens_text:
                result_parts.append("\n\n" + lens_text)
                debug_info["layers"].append(f"lens_resolved:{archetype.value}")
        else:
            # Legacy/Fallback behavior
            if archetype != Archetype.NEUTRAL and archetype.value in lens_data:
                lens_text = lens_data[archetype.value]
                result_parts.append("\n\n" + lens_text)
                debug_info["layers"].append(f"lens:{archetype.value}")
            elif archetype != Archetype.NEUTRAL:
                # Apply micro-overlay if no full lens text
                micro = self._apply_micro_overlay(text_to_use, archetype)
                if micro != text_to_use:
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
            # Check if this insert is specific to a mode
            req_thermal = insert_data.get("condition", {}).get("thermal_mode")
            if req_thermal is not None:
                # If insert specifies thermal requirement
                if req_thermal != thermal_mode:
                    continue

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
        final_parts = [text_to_use]

        # After base inserts
        for insert in after_base_inserts:
            final_parts.append("\n" + insert)

        # Lens text
        if lens_text:
            final_parts.append("\n\n" + lens_text)
        elif not lens_text and not lens_data and archetype != Archetype.NEUTRAL and "micro_overlay" in str(debug_info["layers"]):
            # Only apply generic atmosphere if no specific lens text was found/resolved
            final_parts.append("\n\n" + MICRO_OVERLAYS[archetype]["atmosphere"])

        # After lens inserts
        for insert in after_lens_inserts:
            final_parts.append("\n" + insert)

        # Before choices inserts
        for insert in before_choices_inserts:
            final_parts.append("\n\n" + insert)

        full_text = "".join(final_parts)

        # === LAYER 3.5: THEORY COMMENTARY ===
        theory_commentary = []
        if self.skill_system and player_state.get("active_theories"):
            theory_commentary = self.skill_system.check_theory_commentary(player_state["active_theories"])
            
        for comm in theory_commentary:
            comm_text = f"\n\n{Colors.MAGENTA}[{comm['skill'].upper()}]: \"{comm['text']}\"{Colors.RESET}"
            full_text += comm_text
            debug_info["layers"].append(f"theory:{comm['skill']}")

        # === LAYER 3.6: PARAGRAPH-SPECIFIC INSERTS ===
        # Handle AFTER_PARAGRAPH:n
        for insert_data in inserts_data:
            pos_str = insert_data.get("insert_at", "")
            if pos_str.startswith("AFTER_PARAGRAPH:"):
                if self._check_insert_condition(insert_data.get("condition", {}), player_state):
                    try:
                        p_idx = int(pos_str.split(":")[1])
                        paragraphs = full_text.split("\n\n")
                        if 0 <= p_idx < len(paragraphs):
                            paragraphs[p_idx] += " " + insert_data.get("text", "")
                            full_text = "\n\n".join(paragraphs)
                    except (ValueError, IndexError):
                        pass

        # === LAYER 4: FRACTURE EFFECTS ===
        fracture_applied = False
        if self._should_apply_fracture(player_state):
            full_text = self._apply_fracture_effect(full_text, player_state)
            fracture_applied = True
            debug_info["layers"].append("fracture")

        # === LAYER 5: DEVELOPER COMMENTARY ===
        if self.developer_commentary:
            dev_note = text_data.get("dev_note")
            if dev_note:
                full_text += f"\n\n{Colors.CYAN}[DEV NOTE: {dev_note}]{Colors.RESET}"

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
        """
        if archetype not in MICRO_OVERLAYS:
            return text

        overlay = MICRO_OVERLAYS[archetype]
        return overlay["atmosphere"]

    def _check_insert_condition(self, condition: dict, state: Any) -> bool:
        """Check if an insert's condition is met."""
        if not condition:
            return True

        # Handle GameState object or dict
        is_gs = hasattr(state, 'get_effective_skill')
        
        # Skill threshold check: skill_gte
        skill_gte = condition.get("skill_gte", {})
        for skill_name, threshold in skill_gte.items():
            if is_gs:
                val = state.get_effective_skill(skill_name)
            else:
                val = self._get_skill_value(skill_name, state)
            if val < threshold:
                return False

        # Flag check
        flag_set = condition.get("flag_set")
        if flag_set:
            flags = state.flags if is_gs else state.get("flags", {})
            if isinstance(flags, (set, list)):
                if flag_set not in flags: return False
            elif isinstance(flags, dict):
                if not flags.get(flag_set): return False

        # Theory active check (In board_graph nodes)
        theory_active = condition.get("theory_active")
        if theory_active:
            if is_gs:
                if not any(n["id"] == theory_active for n in state.board_graph["nodes"]):
                    return False
            else:
                active_theories = state.get("active_theories", [])
                if theory_active not in active_theories:
                    return False

        # Trust threshold check
        trust_gte = condition.get("trust_gte", {})
        for npc_id, threshold in trust_gte.items():
            trust_levels = state.trust if is_gs else state.get("trust", {})
            if trust_levels.get(npc_id, 0) < threshold:
                return False

        # Attention threshold check
        attention_gte = condition.get("attention_gte")
        if attention_gte is not None:
            att = state.attention_meter if is_gs else state.get("attention", 0)
            if att < attention_gte:
                return False

        # Equipment check
        equipment = condition.get("equipment")
        if equipment:
            inv = state.inventory if is_gs else state.get("inventory", [])
            if equipment not in inv:
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

    def _should_apply_fracture(self, state: Any) -> bool:
        """
        Determine if a reality fracture should occur.
        Fractures are rare and triggered by attention/flags/storms.
        """
        is_gs = hasattr(state, 'modify_sanity')
        
        # Check explicit fracture flag
        flags = state.flags if is_gs else state.get("flags", {})
        if isinstance(flags, (set, list, dict)):
            if "trigger_fracture" in flags:
                if isinstance(flags, dict):
                    if flags.get("trigger_fracture"): return True
                else:
                    return True

        # Check attention threshold
        attention = state.attention_meter if is_gs else state.get("attention", 0)
        if attention >= 75:
            import random
            return random.random() < 0.15  # 15% chance at high attention

        # Base random chance (very low)
        if self.fracture_chance > 0:
            import random
            return random.random() < self.fracture_chance

        return False

    def _apply_fracture_effect(self, text: str, state: Any) -> str:
        """
        Apply a reality fracture effect to the text.
        These are subtle wrongnesses that break the fourth wall or reality.
        """
        import random

        fracture_types = [
            self._fracture_timestamp,
            self._fracture_repetition,
            self._fracture_wrong_name,
            self._fracture_extra_paragraph,
            self._fracture_static_overlay,
            self._fracture_missing_words
        ]

        # Choose a random fracture type
        fracture = random.choice(fracture_types)
        return fracture(text, state)

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

    def _fracture_wrong_name(self, text: str, state: Any) -> str:
        """Briefly use the wrong name."""
        is_gs = hasattr(state, 'flags')
        player_name = getattr(state, "name", "you") if is_gs else state.get("player_name", "you")
        wrong_names = ["[REDACTED]", "the other one", "█████", "yourself"]
        import random
        # Simple replacement - in real implementation, would be more sophisticated
        return text + f"\n\n[{random.choice(wrong_names)} continues...]"

    def _fracture_extra_paragraph(self, text: str, state: Any) -> str:
        """Add an impossible paragraph."""
        extras = [
            "\n\n(You remember writing this. But you haven't yet.)",
            "\n\n[This section appears to be from a different document entirely.]",
            "\n\nYou skip ahead. The page is blank. You go back. The words are different now.",
            "\n\n[Note: The investigator is reminded that they are not the first. They are not the last.]"
        ]
        import random
        return text + random.choice(extras)

    def _fracture_static_overlay(self, text: str, state: Any) -> str:
        """Add 'static' noise to the text."""
        noise_chars = ["▓", "▒", "░", "█", "▄", "▀", "▌", "▐"]
        import random
        text_list = list(text)
        for _ in range(int(len(text) * 0.05)):
            idx = random.randint(0, len(text_list) - 1)
            if text_list[idx] not in ["\n", " "]:
                text_list[idx] = random.choice(noise_chars)
        return "".join(text_list)

    def _fracture_missing_words(self, text: str, state: Any) -> str:
        """Replace some words with blank spaces."""
        words = text.split(" ")
        import random
        for _ in range(int(len(words) * 0.1)):
            idx = random.randint(0, len(words) - 1)
            words[idx] = " " * len(words[idx])
        return " ".join(words)


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
                     player_state: dict = None, npc: Any = None) -> Tuple[str, str]:
        """
        Compose a dialogue line.
        Returns (speaker, composed_text).

        Args:
            line_data: The dialogue node data
            archetype: Player's lens archetype
            player_state: Player state dict
            npc: Optional NPC object for tone modulation (Week 25)
        """
        speaker = line_data.get("speaker", "???")

        # Compose the dialogue text
        text_data = line_data.get("text", {})
        if isinstance(text_data, str):
            text_data = {"base": text_data}

        # Week 25: Tone Modulation
        # Skills affect tone without direct player control.
        # We append tone descriptors based on player skills if applicable.

        mod_suffix = ""

        if self.composer.skill_system:
            # High Authority -> Commanding Tone perception
            auth = self.composer.skill_system.get_skill_total("Authority")
            if auth >= 5:
                # If speaker is ambiguous or hostile, Authority clarifies dominance
                if npc and npc.get_relationship_status() == "hostile":
                    mod_suffix += " (submitting)"

            # Low Composure -> Perception of chaos
            comp = self.composer.skill_system.get_skill_total("Composure")
            if comp <= 1:
                # Player perceives things as more erratic
                mod_suffix += " (distorted)"

        result = self.composer.compose(text_data, archetype, player_state)
        full_text = result.full_text

        # Apply speaker-specific lens
        if archetype == Archetype.HAUNTED:
            if "lens" not in line_data.get("text", {}):
                speaker = f"{speaker} (familiar)"

        # Week 25: NPC Response Modulation (Trust/Fear/Rapport)
        if npc:
            if npc.fear > 70:
                mod_suffix += " (shaking)"
            elif npc.trust < 20:
                mod_suffix += " (cold)"
            elif npc.rapport > 60:
                mod_suffix += " (warm)"

        if mod_suffix:
            speaker += mod_suffix

        return speaker, full_text


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
