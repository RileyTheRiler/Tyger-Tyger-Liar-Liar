"""
Text Composer - The "Bad Blood" Narrative Engine.
Composes scene text from: base + lens overlay + skill-based inserts + fracture effects.
Allows writing one scene with multiple interpretations without tripling workload.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# Import Colors for theory commentary formatting
try:
    from ui.interface import Colors
except ImportError:
    # Fallback if running standalone
    class Colors:
        MAGENTA = "\033[35m"
        RESET = "\033[0m"

from engine.distortion_rules import DistortionManager
from engine.echo_manager import EchoManager
from engine.skill_voice_manager import SkillVoiceManager


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
    inserts_applied: List[str]
    fracture_applied: bool
    raw_text: Optional[str] = None # Pre-distortion text for side-by-side comparison
    lens_used: Optional[str] = None
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

    def __init__(self, skill_system=None, board=None, game_state=None, hallucination_engine=None):
        self.skill_system = skill_system
        self.board = board
        self.game_state = game_state
        self.hallucination_engine = hallucination_engine
        self.debug_mode = False
        self.developer_commentary = False
        self.distortion_manager = DistortionManager()
        self.echo_manager = EchoManager()
        self.skill_voice_manager = SkillVoiceManager()
        self.fracture_chance = 0.01  # Base chance for reality glitches

    
    def calculate_dominant_lens(self, player_state: dict = None) -> Archetype:
        """
        Calculate the dominant lens based on player's skills and active theories.
        Week 12: Dynamic lens selection.
        
        Returns:
            Archetype based on dominant attribute and active theories
        """
        if not self.skill_system or player_state is None:
            return Archetype.NEUTRAL
        
        # Calculate dominant attribute scores
        intuition_skills = ["Paranormal Sensitivity", "Instinct", "Subconscious", "Pattern Recognition"]
        reason_skills = ["Logic", "Skepticism", "Forensics", "Research"]
        presence_skills = ["Authority", "Interrogation", "Cool", "Composure"]
        
        intuition_total = sum(
            self.skill_system.get_skill(s).effective_level 
            for s in intuition_skills 
            if self.skill_system.get_skill(s)
        ) + (self.skill_system.attributes["INTUITION"].value * 2)

        reason_total = sum(
            self.skill_system.get_skill(s).effective_level 
            for s in reason_skills 
            if self.skill_system.get_skill(s)
        ) + (self.skill_system.attributes["REASON"].value * 2)

        presence_total = sum(
            self.skill_system.get_skill(s).effective_level
            for s in presence_skills
            if self.skill_system.get_skill(s)
        ) + (self.skill_system.attributes["PRESENCE"].value * 2)
        
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
            haunted_count = sum(1 for t in haunted_theories if t in active_theories) # Corrected order
            
            # Theory override (theories are stronger than skills)
            if haunted_count > 0:
                return Archetype.HAUNTED
            if believer_count > skeptic_count:
                return Archetype.BELIEVER
            if skeptic_count > believer_count:
                return Archetype.SKEPTIC
        
        # Combined scores
        scores = {
            Archetype.BELIEVER: intuition_total,
            Archetype.SKEPTIC: reason_total,
            Archetype.HAUNTED: presence_total
        }
        
        dominant = max(scores, key=scores.get)
        max_val = scores[dominant]
        other_vals = [v for k, v in scores.items() if k != dominant]

        if max_val >= max(other_vals) + 3:
            return dominant
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
            
        # Calculate Dissonance (Used in multiple layers)
        dissonance = 0.0
        pop_system = player_state.get("population_system")
        if pop_system and hasattr(pop_system, "get_dissonance_factor"):
            dissonance = pop_system.get_dissonance_factor()
            
        # === LAYER 1: BASE TEXT vs THERMAL ===
        base_text = text_data.get("base", "")
        thermal_text = text_data.get("thermal", "")
        
        # Thermal Logic: If active and available, it usually replaces or heavily modifies base
        # But we might want to keep base if thermal is just an add-on. 
        # Design implies profound shift. Let's prioritize thermal if present.
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

        # === LAYER 2: LENS OVERLAY ===
        # Lenses might still apply in thermal mode, but maybe filtered?
        # A "Believer" sees ghosts in the heat signatures. 
        # So yes, we keep Lens layers.
        lens_text = None
        lens_data = text_data.get("lens", {})

        if archetype != Archetype.NEUTRAL and archetype.value in lens_data:
            lens_text = lens_data[archetype.value]
            result_parts.append("\n\n" + lens_text)
            debug_info["layers"].append(f"lens:{archetype.value}")
        elif archetype != Archetype.NEUTRAL:
            # Apply micro-overlay if no full lens text
            # In thermal mode, micro-overlays might be weird, but let's keep for consistency
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
        elif archetype != Archetype.NEUTRAL and "micro_overlay" in str(debug_info["layers"]):
            micro = self._apply_micro_overlay(base_text, archetype) # Use base for micro context?
            # Actually strictly adding atmosphere string
            final_parts.append("\n\n" + MICRO_OVERLAYS[archetype]["atmosphere"])

        # After lens inserts
        for insert in after_lens_inserts:
            final_parts.append("\n" + insert)

        # Before choices inserts
        for insert in before_choices_inserts:
            final_parts.append("\n\n" + insert)

        full_text = "".join(final_parts)

        # === LAYER 3.5: INTERNAL MONOLOGUE (Skills, Theories, Hallucinations) ===
        # Unify all internal voices into a structured flow
        internal_voices = []
        
        # 1. Theories (Internalized thoughts)
        if self.skill_system and player_state.get("active_theories"):
            sanity = player_state.get("sanity", 100.0)
            theory_commentary = self.skill_system.check_theory_commentary(player_state["active_theories"], sanity)
            for comm in theory_commentary:
                internal_voices.append({
                    "skill": comm["skill"].upper(),
                    "text": comm["text"],
                    "color": comm.get("color", Colors.MAGENTA),
                    "type": "theory"
                })

        # 2. Skill Interjections (Passive checks)
        if self.skill_system:
            sanity = player_state.get("sanity", 100.0)
            sanity_tier = self._get_sanity_tier(player_state)
            skill_interrupts = self.skill_system.check_passive_interrupts(full_text, sanity, current_archetype=archetype.value if archetype else None)
            for interrupt in skill_interrupts:
                if interrupt.get("type") == "argument":
                    # Special handling for internal arguments
                    arg_text = f"\n\n[INTERNAL CONFLICT]: {interrupt['text']}"
                    for s_voice in interrupt["skills"]:
                        # Enhance argument voices
                        attr = self._get_skill_attribute(s_voice['skill'])
                        enhanced = self.skill_voice_manager.get_skill_specific_voice(s_voice['skill'], attr, full_text, sanity_tier, dissonance=dissonance)
                        v_text = enhanced['text'] if enhanced else s_voice['text']
                        arg_text += f"\n  - {s_voice['skill']}: \"{v_text}\""
                    full_text += arg_text
                    debug_info["layers"].append("skill_argument")
                else:
                    # Enhance standard interjection
                    attr = self._get_skill_attribute(interrupt['skill'])
                    enhanced = self.skill_voice_manager.get_skill_specific_voice(interrupt['skill'], attr, full_text, sanity_tier, dissonance=dissonance)
                    
                    if enhanced:
                        internal_voices.append({
                            "skill": interrupt["skill"],
                            "text": enhanced["text"],
                            "color": enhanced.get("color", Colors.RESET),
                            "type": "skill"
                        })
                    else:
                        internal_voices.append({
                            "skill": interrupt["skill"],
                            "text": interrupt["text"],
                            "color": interrupt.get("color", Colors.RESET),
                            "type": "skill"
                        })

        # 3. Hallucinations & Competing Voices (Low Sanity)
        if self.hallucination_engine:
            sanity_tier = self._get_sanity_tier(player_state)
            instability = player_state.get("instability", False)
            competing_voices = self.hallucination_engine.get_competing_voices(full_text, sanity_tier, instability)
            for voice in competing_voices:
                internal_voices.append({
                    "skill": voice["skill"].upper(),
                    "text": voice["text"],
                    "color": Colors.RED if voice["skill"] == "Paranoia" else Colors.RESET,
                    "type": "hallucination"
                })

        # 4. Weave Voices into Narrative
        # Sanity-based corruption filter for voices
        sanity = player_state.get("sanity", 100.0)
        for voice in internal_voices:
            voice_text = voice["text"]
            
            # Apply corruption if sanity is extremely low
            if sanity < 20:
                voice_text = self._corrupt_voice_text(voice_text, sanity)
            
            # Inject into text
            formatted_voice = f"\n\n{voice['color']}[{voice['skill']}]: \"{voice_text}\"{Colors.RESET}"
            full_text += formatted_voice
            debug_info["layers"].append(f"voice:{voice['skill']}")

        # === LAYER 3.6: ECHO SYSTEM ===
        echo_modifiers = self.echo_manager.get_narrative_modifiers()
        if echo_modifiers:
            full_text = self._apply_echoes(full_text, echo_modifiers)
            debug_info["layers"].append("echoes")

        # === LAYER 4: FRACTURE EFFECTS & DISTORTION ===
        raw_text_content = full_text
        fracture_applied = False

        # Check for active failures
        active_failures = player_state.get("active_failures", [])

        # Cognitive Overload: Fragment text
        if "cognitive_overload" in active_failures:
            full_text = self._apply_overload_fragmentation(full_text)
            debug_info["layers"].append("cognitive_overload")

        # Social Breakdown: Paranoia
        if "social_breakdown" in active_failures:
            full_text = self._apply_paranoia(full_text)
            debug_info["layers"].append("social_breakdown")

        # Investigative Paralysis: Circular text
        if "investigative_paralysis" in active_failures:
            full_text = self._apply_paralysis_loops(full_text)
            debug_info["layers"].append("investigative_paralysis")

        # Reality Fractures
        if self._should_apply_fracture(player_state):
            full_text = self._apply_fracture_effect(full_text, player_state)
            debug_info["layers"].append("fracture")

        # Evidence Permeation (Echoes)
        if self.board and player_state.get("active_theories"):
            full_text = self._apply_evidence_echoes(full_text, player_state["active_theories"])
            debug_info["layers"].append("evidence_echoes")

        # Stress-based Distortions
        if self.distortion_manager and player_state:
            full_text = self.distortion_manager.apply_distortions(full_text, player_state, archetype.value if archetype else None)

        # Population Dissonance (347 Rule)
        if dissonance > 0:
            full_text = self._apply_dissonance_glitches(full_text, dissonance)
            debug_info["layers"].append(f"dissonance:{dissonance:.2f}")

        fracture_applied = (full_text != raw_text_content)
        if fracture_applied and "fracture" not in debug_info["layers"]:
            debug_info["layers"].append("distortion")


        # === LAYER 5: DEVELOPER COMMENTARY ===
        if self.developer_commentary:
            dev_note = text_data.get("dev_note")
            if dev_note:
                full_text += f"\n\n{Colors.CYAN}[DEV NOTE: {dev_note}]{Colors.RESET}"

            # Show active flags affecting this scene?
            # Or insert conditions?
            # Maybe too verbose. Just explicit dev_note is good.

        return ComposedText(
            full_text=full_text.strip(),
            raw_text=raw_text_content.strip(),
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

    def _get_skill_attribute(self, skill_name: str) -> str:
        """Helper to find which attribute a skill belongs to."""
        if not self.skill_system:
            return "REASON" # Fallback
            
        skill = self.skill_system.get_skill(skill_name.title())
        if skill and hasattr(skill, 'attribute_ref'):
            return skill.attribute_ref.name
        return "REASON"

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

        # Narrative Entropy Scaling
        entropy = getattr(state, "narrative_entropy", 0.0) if is_gs else state.get("narrative_entropy", 0.0)
        entropy_modifier = entropy / 500.0 # Subtly increases base chance (up to +0.2 at 100 entropy)
        
        # Base random chance
        chance = self.fracture_chance + entropy_modifier
        if chance > 0:
            import random
            return random.random() < chance

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

    def _apply_dissonance_glitches(self, text: str, intensity: float) -> str:
        """
        Apply glitches based on Population Dissonance (347 Rule).
        
        Intensity 0.0 - 1.0
        Effects:
        - Word stuttering ("The the")
        - Character swaps ("wih sper")
        - Number injection ("347")
        - Punctuation corruption
        """
        import random
        
        words = text.split()
        if not words: return text
        
        new_words = []
        
        for w in words:
            # 1. Stutter (Repetition) - Increases with intensity
            if random.random() < intensity * 0.15:
                w = f"{w} {w}"
            
            # 2. Character Swaps (Typos) - Higher intensity only
            if intensity > 0.4 and len(w) > 3 and random.random() < intensity * 0.1:
                # Swap two chars
                idx = random.randint(0, len(w)-2)
                char_list = list(w)
                char_list[idx], char_list[idx+1] = char_list[idx+1], char_list[idx]
                w = "".join(char_list)
            
            # 3. Number Injection (The Echo of 347)
            if intensity > 0.6 and random.random() < intensity * 0.05:
                w = f"{w} (347)"
            elif intensity > 0.8 and random.random() < 0.02:
                w = "347"
                
            new_words.append(w)
            
        result = " ".join(new_words)
        
        # 4. Terminal Entropy (High Intensity Punctuation Decay)
        if intensity > 0.9:
            result = result.replace(".", "...")
            result = result.replace(",", "...")
            
        return result

    def _fracture_timestamp(self, text: str, _state: dict) -> str:
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

    def _apply_overload_fragmentation(self, text: str) -> str:
        """Simulate cognitive overload by truncating and fragmenting text."""
        # Split into sentences
        sentences = text.split(". ")
        if len(sentences) <= 1: return text

        # Keep only the beginning or random parts
        import random
        if random.random() < 0.5:
            # Just fade out
            return ". ".join(sentences[:2]) + "... [FOCUS LOST]"
        else:
            # Fragmented
            new_text = ""
            for s in sentences:
                if random.random() < 0.5:
                    new_text += s + ". "
                else:
                    new_text += "... "
            return new_text.strip()

    def _apply_paralysis_loops(self, text: str) -> str:
        """Simulate analysis paralysis by repeating doubts."""
        doubt_phrases = [
            "\n\nBut that can't be right.",
            "\n\nWait. Is this significant?",
            "\n\nYou're missing something.",
            "\n\nReview the data again."
        ]
        import random
        return text + random.choice(doubt_phrases)

    def _apply_paranoia(self, text: str) -> str:
        """Inject paranoid thoughts for social breakdown."""
        paranoia_phrases = [
            " (They are lying to you.)",
            " (Do not trust them.)",
            " (They know what you did.)",
            " (Can you hear them whispering?)"
        ]
        import random
        # Insert randomly into text
        if random.random() < 0.4:
            return text + random.choice(paranoia_phrases)
        return text

    def _apply_echoes(self, text: str, echoes: List[Dict]) -> str:
        """Subtly inject echo motifs into the narrative text."""
        import random
        
        # We don't want to overwhelm every sentence.
        # Let's pick 1-2 echoes to emphasize if many are active.
        active_sample = random.sample(echoes, min(2, len(echoes)))
        
        paragraphs = text.split("\n\n")
        
        for echo in active_sample:
            content = echo["content"]
            m_type = echo["type"]
            intensity = echo["intensity"]
            
            # Injection strategies based on motif type
            if m_type == "smell":
                # Inject as an adjective or atmosphere
                if random.random() < 0.5 and paragraphs:
                    paragraphs[0] += f" The air is tainted by a {content} scent."
            elif m_type == "sound":
                if len(paragraphs) > 1:
                    paragraphs[1] += f" Beneath the surface, you hear a {content} sound."
            elif m_type == "visual":
                # Blurry edges or flickering
                pass # Already handled by shaders in UI usually, but let's add text
                if random.random() < 0.3:
                    text_to_add = f" Your vision dances with {content}."
                    paragraphs[-1] += text_to_add
            elif m_type == "thought":
                # Direct internal monologue
                text_to_add = f" ({content}...)"
                if paragraphs:
                    idx = random.randint(0, len(paragraphs) - 1)
                    paragraphs[idx] += text_to_add
                    
        return "\n\n".join(paragraphs)

    def _apply_evidence_echoes(self, text: str, active_theories: List[str]) -> str:
        """
        Highlight keywords from evidence linked to active theories.
        Shows how the investigator's mind keeps circling back to their evidence.
        """
        if not self.board:
            return text
            
        # Collect all keywords from evidence linked to active theories
        keywords = set()
        for tid in active_theories:
            theory = self.board.get_theory(tid)
            if theory and (theory.status == "active" or theory.status == "internalizing"):
                for ev_id in theory.linked_evidence:
                    # Treat evidence IDs as keywords for now (e.g. "red_car" -> "red car")
                    clean_keyword = ev_id.replace("_", " ").lower()
                    keywords.add(clean_keyword)
                    # Also individual words from longer keywords
                    for word in clean_keyword.split():
                        if len(word) > 3: # Only significant words
                            keywords.add(word)
        
        if not keywords:
            return text
            
        import re
        # Sort keywords by length descending to match longest phrases first
        sorted_keywords = sorted(list(keywords), key=len, reverse=True)
        
        # Case insensitive replacement with a subtle highlight (e.g. bold or italic)
        # We'll use a regex for boundaries
        for kw in sorted_keywords:
            pattern = re.compile(rf'\b({re.escape(kw)})\b', re.IGNORECASE)
            # Subtle highlight: wrapping in brackets or italics
            # For "Tyger" we use italics to show obsession
            text = pattern.sub(r'*\1*', text)
            
        return text

    def _get_sanity_tier(self, state: dict) -> int:
        """Helper to get 0-4 sanity tier."""
        sanity = state.get("sanity", 100.0)
        if sanity >= 75: return 4
        if sanity >= 50: return 3
        if sanity >= 25: return 2
        if sanity >= 10: return 1
        return 0

    def _corrupt_voice_text(self, text: str, sanity: float) -> str:
        """Apply reality-warping corruption to voice text at low sanity."""
        import random
        corruption_chars = ["█", "▓", "░", "ERROR", "?", "!", "..."]
        
        words = text.split()
        corrupted_words = []
        
        # Chance to replace words increases as sanity drops below 20
        chance = (20.0 - sanity) / 20.0
        
        for word in words:
            if random.random() < (chance * 0.4):
                corrupted_words.append(random.choice(corruption_chars))
            else:
                corrupted_words.append(word)
                
        return " ".join(corrupted_words)


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
