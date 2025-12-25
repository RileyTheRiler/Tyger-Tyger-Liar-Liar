"""
Clue System - Manages clue discovery, passive perception, and Board integration.
Investigation is skill-gated and text-forward per Canon & Constraints.
No pixel hunting - clues appear automatically when thresholds are met.
"""

import json
import os
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum


class ClueReliability(Enum):
    UNRELIABLE = 0.2
    QUESTIONABLE = 0.4
    MODERATE = 0.6
    RELIABLE = 0.8
    CERTAIN = 1.0


@dataclass
class ClueTheoryLink:
    """Link between a clue and a theory."""
    theory_id: str
    relation: str  # "supports", "contradicts", "associated"


@dataclass
class Clue:
    """A discovered or discoverable clue."""
    id: str
    title: str
    text: dict  # Base + lens variants
    source_scene_id: str
    tags: List[str] = field(default_factory=list)
    reliability: float = 0.5
    links_to_theories: List[ClueTheoryLink] = field(default_factory=list)
    related_npcs: List[str] = field(default_factory=list)
    related_locations: List[str] = field(default_factory=list)
    analysis_skills: List[str] = field(default_factory=list)
    # Deprecated fields (moved to ClueState)
    analyzed: bool = False
    analysis_result: Optional[dict] = None

    def get_text(self, lens: str = "neutral") -> str:
        """Get clue text for the current lens."""
        if isinstance(self.text, str):
            return self.text

        lens_text = self.text.get("lens", {})
        if lens in lens_text:
            return lens_text[lens]
        return self.text.get("base", str(self.text))

    def get_base_text(self) -> str:
        """Get the base observation text."""
        if isinstance(self.text, str):
            return self.text
        return self.text.get("base", "")


@dataclass
class ClueState:
    """The state of a specific acquired clue."""
    clue_id: str
    raw_observation: str
    current_interpretation: str
    current_lens: str  # The lens used for interpretation
    confidence: float
    analyzed: bool = False
    analysis_result: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "clue_id": self.clue_id,
            "raw_observation": self.raw_observation,
            "current_interpretation": self.current_interpretation,
            "current_lens": self.current_lens,
            "confidence": self.confidence,
            "analyzed": self.analyzed,
            "analysis_result": self.analysis_result
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ClueState':
        return cls(
            clue_id=data["clue_id"],
            raw_observation=data["raw_observation"],
            current_interpretation=data["current_interpretation"],
            current_lens=data.get("current_lens", "neutral"),
            confidence=data.get("confidence", 0.5),
            analyzed=data.get("analyzed", False),
            analysis_result=data.get("analysis_result")
        )


@dataclass
class PassiveClueCheck:
    """Definition of a passive clue check in a scene."""
    clue_id: str
    reveal_text: Optional[str]
    conditions: dict = field(default_factory=dict)


class ClueSystem:
    """
    Manages clue discovery and passive perception.

    Passive Perception Flow:
    1. Scene loads
    2. Evaluate passive perception for each clue in scene
    3. If skill >= threshold OR equipment present → reveal clue
    4. Append clue text to narrative + add to Board
    """

    def __init__(self, clues_dir: str = None, board=None):
        self.clue_definitions: Dict[str, Clue] = {}
        # Changed from Set[str] to Dict[str, ClueState]
        self.acquired_clues: Dict[str, ClueState] = {}
        self.board = board

        if clues_dir:
            self.load_clues(clues_dir)

    def load_clues(self, clues_dir: str):
        """Load clue definitions from a directory."""
        if not os.path.exists(clues_dir):
            return

        for filename in os.listdir(clues_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(clues_dir, filename), 'r') as f:
                        data = json.load(f)

                    clues = data if isinstance(data, list) else [data]
                    for clue_data in clues:
                        self._load_clue(clue_data)
                except Exception as e:
                    print(f"Error loading clues from {filename}: {e}")

    def _load_clue(self, data: dict) -> Clue:
        """Load a single clue from data."""
        links = []
        for link in data.get("links_to_theories", []):
            if isinstance(link, str):
                links.append(ClueTheoryLink(
                    theory_id=link,
                    relation="associated"
                ))
            else:
                links.append(ClueTheoryLink(
                    theory_id=link["theory_id"],
                    relation=link.get("relation", "associated")
                ))

        clue = Clue(
            id=data["id"],
            title=data["title"],
            text=data.get("text", {"base": ""}),
            source_scene_id=data.get("source_scene_id", ""),
            tags=data.get("tags", []),
            reliability=data.get("reliability", 0.5),
            links_to_theories=links,
            related_npcs=data.get("related_npcs", []),
            related_locations=data.get("related_locations", []),
            analysis_skills=data.get("analysis_skills", [])
        )

        self.clue_definitions[clue.id] = clue
        return clue

    def register_clue(self, clue_data: dict) -> Clue:
        """Register a new clue definition."""
        return self._load_clue(clue_data)

    def get_clue(self, clue_id: str) -> Optional[Clue]:
        """Get a clue definition by ID."""
        return self.clue_definitions.get(clue_id)

    def has_clue(self, clue_id: str) -> bool:
        """Check if player has acquired a clue."""
        return clue_id in self.acquired_clues

    def get_acquired_clue(self, clue_id: str) -> Optional[ClueState]:
        """Get the state of an acquired clue."""
        return self.acquired_clues.get(clue_id)

    def acquire_clue(self, clue_id: str, lens: str = "neutral") -> Optional[ClueState]:
        """
        Acquire a clue if not already acquired.
        Returns the ClueState if newly acquired, None if already had it.
        """
        if clue_id in self.acquired_clues:
            return None

        clue_def = self.get_clue(clue_id)
        if not clue_def:
            return None

        # Create new clue state with initial interpretation
        state = ClueState(
            clue_id=clue_id,
            raw_observation=clue_def.get_base_text(),
            current_interpretation=clue_def.get_text(lens),
            current_lens=lens,
            confidence=clue_def.reliability,
            analyzed=False,
            analysis_result=None
        )

        self.acquired_clues[clue_id] = state
        print(f"[CLUE] Acquired: {clue_def.title} (Lens: {lens})")

        # Add to Board if available
        if self.board:
            self._add_clue_to_board(clue_def)

        return state

    def reinterpret_clue(self, clue_id: str, new_lens: str) -> Optional[ClueState]:
        """
        Update the interpretation of an existing clue.
        Returns the updated ClueState, or None if not found/no change.
        """
        if clue_id not in self.acquired_clues:
            return None

        state = self.acquired_clues[clue_id]
        if state.current_lens == new_lens:
            return None

        clue_def = self.get_clue(clue_id)
        if not clue_def:
            return None

        state.current_lens = new_lens
        state.current_interpretation = clue_def.get_text(new_lens)

        print(f"[CLUE] Reinterpreted: {clue_def.title} as {new_lens.upper()}")
        return state

    def _add_clue_to_board(self, clue: Clue):
        """Add a clue node to the Board and link it."""
        # This would integrate with the Board system
        # For now, we'll just print the action
        print(f"[BOARD] Added clue node: {clue.title}")

        # Auto-link based on theory links
        for link in clue.links_to_theories:
            print(f"[BOARD] Linked clue to theory '{link.theory_id}' ({link.relation})")

        # Auto-link based on tags
        for tag in clue.tags:
            print(f"[BOARD] Tagged clue with: {tag}")

    def evaluate_passive_clues(self, scene_passive_clues: List[dict],
                                player_state: dict, lens_system=None) -> List[Tuple[ClueState, str]]:
        """
        Evaluate passive clue checks for a scene.

        Args:
            scene_passive_clues: List of passive clue definitions from scene
            player_state: Dict with skills, inventory, equipment, active_theories, flags
            lens_system: Optional LensSystem to determine interpretation

        Returns:
            List of (ClueState, reveal_text) tuples for clues that should be revealed
        """
        revealed = []

        # Determine lens
        current_lens = "neutral"
        if lens_system:
            current_lens = lens_system.calculate_lens()
        elif "archetype" in player_state:
             current_lens = player_state["archetype"].lower()

        for pc_data in scene_passive_clues:
            clue_id = pc_data.get("clue_id")
            if not clue_id or self.has_clue(clue_id):
                continue

            conditions = pc_data.get("visible_when", {})

            if self._check_visibility_conditions(conditions, player_state):
                state = self.acquire_clue(clue_id, current_lens)
                if state:
                    clue_def = self.get_clue(clue_id)
                    reveal_text = pc_data.get("reveal_text") or state.current_interpretation
                    revealed.append((state, reveal_text))

        return revealed

    def _check_visibility_conditions(self, conditions: dict, player_state: dict) -> bool:
        """Check if visibility conditions are met for a passive clue."""
        if not conditions:
            return True

        # Skill threshold check
        skill_gte = conditions.get("skill_gte", {})
        for skill_name, threshold in skill_gte.items():
            player_skill = player_state.get("skills", {}).get(skill_name, 0)
            if player_skill < threshold:
                return False

        # Equipment check
        equipment = conditions.get("equipment")
        if equipment:
            inventory = player_state.get("inventory", [])
            equipped = player_state.get("equipped", [])
            if equipment not in inventory and equipment not in equipped:
                return False

        # Theory active check
        theory_active = conditions.get("theory_active")
        if theory_active:
            active_theories = player_state.get("active_theories", [])
            if theory_active not in active_theories:
                return False

        # Flag set check
        flag_set = conditions.get("flag_set")
        if flag_set:
            flags = player_state.get("flags", {})
            if not flags.get(flag_set, False):
                return False

        return True

    def format_revealed_clues(self, revealed: List[Tuple[ClueState, str]], lens: str = "neutral") -> str:
        """Format revealed clues for narrative insertion."""
        if not revealed:
            return ""

        parts = []
        for state, reveal_text in revealed:
            parts.append(f"\n[You notice something...]\n{reveal_text}")

        return "\n".join(parts)

    def analyze_clue(self, clue_id: str, skill_name: str, skill_level: int,
                     dc: int = 9) -> dict:
        """
        Attempt to analyze a clue for more information.

        Returns dict with success status and any revealed information.
        """
        state = self.get_acquired_clue(clue_id)
        if not state:
            return {"success": False, "error": "Clue not acquired"}

        if state.analyzed:
            return {"success": True, "already_analyzed": True,
                    "result": state.analysis_result}

        clue_def = self.get_clue(clue_id)
        if not clue_def:
             return {"success": False, "error": "Clue definition missing"}

        if skill_name not in clue_def.analysis_skills:
            return {"success": False, "error": f"{skill_name} cannot analyze this clue"}

        # This would normally integrate with the dice system
        # For now, simple threshold check
        if skill_level >= dc:
            state.analyzed = True
            # Analysis would reveal more based on the clue's analysis_result field
            return {
                "success": True,
                "result": state.analysis_result or {"text": "Analysis complete. No additional details."}
            }
        else:
            return {"success": False, "error": "Analysis failed"}

    def get_clues_by_tag(self, tag: str) -> List[Clue]:
        """Get all acquired clues with a specific tag."""
        return [
            self.clue_definitions[cid]
            for cid in self.acquired_clues.keys()
            if cid in self.clue_definitions and tag in self.clue_definitions[cid].tags
        ]

    def get_clues_for_theory(self, theory_id: str) -> Dict[str, List[Clue]]:
        """Get all acquired clues that link to a theory, grouped by relation."""
        result = {"supports": [], "contradicts": [], "associated": []}

        for clue_id in self.acquired_clues.keys():
            clue = self.clue_definitions.get(clue_id)
            if not clue:
                continue

            for link in clue.links_to_theories:
                if link.theory_id == theory_id:
                    result[link.relation].append(clue)

        return result

    def get_reliability_description(self, reliability: float) -> str:
        """Get human-readable reliability description."""
        if reliability >= 0.9:
            return "Certain"
        elif reliability >= 0.7:
            return "Reliable"
        elif reliability >= 0.5:
            return "Moderate"
        elif reliability >= 0.3:
            return "Questionable"
        else:
            return "Unreliable"

    def get_clue_summary(self) -> List[dict]:
        """Get a summary of all acquired clues."""
        summary = []
        for clue_id, state in self.acquired_clues.items():
            clue = self.clue_definitions.get(clue_id)
            if clue:
                summary.append({
                    "id": clue.id,
                    "title": clue.title,
                    "source": clue.source_scene_id,
                    "tags": clue.tags,
                    "reliability": clue.reliability,
                    "reliability_desc": self.get_reliability_description(clue.reliability),
                    "analyzed": state.analyzed,
                    "theory_links": len(clue.links_to_theories),
                    "interpretation": state.current_interpretation,
                    "lens": state.current_lens
                })
        return summary

    def to_dict(self) -> dict:
        """Serialize clue state for saving."""
        return {
            "acquired_clues": {cid: state.to_dict() for cid, state in self.acquired_clues.items()}
        }

    def restore_state(self, state: dict):
        """Restore clue state from saved data."""
        self.acquired_clues = {}

        # Handle new format
        if "acquired_clues" in state:
            for cid, c_data in state["acquired_clues"].items():
                self.acquired_clues[cid] = ClueState.from_dict(c_data)

        # Handle legacy format (set/list of strings)
        elif "acquired" in state:
            acquired_ids = state.get("acquired", [])
            legacy_states = state.get("states", {})

            for cid in acquired_ids:
                if cid not in self.clue_definitions:
                    continue

                clue_def = self.clue_definitions[cid]
                # Default to neutral if we don't know
                legacy_state = legacy_states.get(cid, {})

                self.acquired_clues[cid] = ClueState(
                    clue_id=cid,
                    raw_observation=clue_def.get_base_text(),
                    current_interpretation=clue_def.get_text("neutral"),
                    current_lens="neutral",
                    confidence=clue_def.reliability,
                    analyzed=legacy_state.get("analyzed", False),
                    analysis_result=legacy_state.get("analysis_result")
                )


# Example clues for testing
EXAMPLE_CLUES = [
    {
        "id": "clue_bloody_glass",
        "title": "Bloody Glass Shard",
        "text": {
            "base": "A piece of window glass, smeared with dried blood. The edges are sharp.",
            "lens": {
                "believer": "The blood forms patterns. Almost like writing. Almost.",
                "skeptic": "Type O negative, based on oxidation. Roughly 72 hours old.",
                "haunted": "You've cut yourself on glass like this before. The memory stings."
            }
        },
        "source_scene_id": "scene_cabin_search",
        "tags": ["physical", "medical", "missing"],
        "reliability": 0.8,
        "links_to_theories": [
            {"theory_id": "the_missing_are_connected", "relation": "supports"}
        ],
        "analysis_skills": ["Forensics", "Medicine"]
    },
    {
        "id": "clue_aurora_photograph",
        "title": "Aurora Photograph",
        "text": {
            "base": "A polaroid of the northern lights. There's something in the aurora. A shape.",
            "lens": {
                "believer": "A face. Multiple faces. Looking down at Kaltvik.",
                "skeptic": "Pareidolia. The human brain sees patterns in randomness.",
                "haunted": "One of those faces is yours. You're certain of it."
            }
        },
        "source_scene_id": "scene_hotel_room",
        "tags": ["photograph", "aurora", "anomaly"],
        "reliability": 0.4,
        "links_to_theories": [
            {"theory_id": "aurora_rules", "relation": "supports"},
            {"theory_id": "347_resonance", "relation": "associated"}
        ],
        "analysis_skills": ["Perception", "Pattern Recognition"]
    },
    {
        "id": "clue_dewline_memo",
        "title": "DEW Line Memo",
        "text": {
            "base": "A partially redacted document from the Defense Early Warning station. Something about 'auditory phenomena' and 'personnel reassignment.'",
            "lens": {
                "believer": "They knew. The government knew about the entity.",
                "skeptic": "Cold War paranoia. Radar operators seeing things that weren't there.",
                "haunted": "The handwriting at the bottom... it looks like yours."
            }
        },
        "source_scene_id": "scene_archive_room",
        "tags": ["document", "dewline", "government"],
        "reliability": 0.7,
        "links_to_theories": [
            {"theory_id": "government_coverup", "relation": "supports"}
        ],
        "analysis_skills": ["Research", "Logic"]
    }
]


if __name__ == "__main__":
    # Test clue system
    system = ClueSystem()

    # Load example clues
    for clue_data in EXAMPLE_CLUES:
        system.register_clue(clue_data)

    print("Registered clues:")
    for clue_id, clue in system.clue_definitions.items():
        print(f"  - {clue.title} ({clue_id})")

    # Test passive perception
    scene_passive_clues = [
        {
            "clue_id": "clue_bloody_glass",
            "visible_when": {"skill_gte": {"Forensics": 2}},
            "reveal_text": "Something catches your eye—a glint of glass under the dresser. Blood-stained."
        },
        {
            "clue_id": "clue_aurora_photograph",
            "visible_when": {"skill_gte": {"Perception": 4}},
        }
    ]

    player_state = {
        "skills": {"Forensics": 3, "Perception": 2},
        "archetype": "skeptic"
    }

    print("\nEvaluating passive clues...")
    revealed = system.evaluate_passive_clues(scene_passive_clues, player_state)

    print(f"Revealed {len(revealed)} clues:")
    for state, text in revealed:
        print(f"  - {system.get_clue(state.clue_id).title}")
        print(f"    Interpretation ({state.current_lens}): \"{state.current_interpretation}\"")

    print("\nAcquired clues:")
    for summary in system.get_clue_summary():
        print(f"  - {summary['title']} (Lens: {summary['lens']})")

    print("\nReinterpreting as Believer...")
    system.reinterpret_clue("clue_bloody_glass", "believer")

    state = system.get_acquired_clue("clue_bloody_glass")
    print(f"  - New Interpretation: \"{state.current_interpretation}\"")
