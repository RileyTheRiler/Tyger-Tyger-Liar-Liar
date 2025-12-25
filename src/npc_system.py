"""
NPC System - Manages non-player characters with trust/fear tracking, relationships, and factions.
Trust is visible, trackable, and consequential per Canon & Constraints.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class FactionAlignment(Enum):
    TRADITIONALIST = "Traditionalist"
    RATIONALIST = "Rationalist"
    PRAGMATIC = "Pragmatic"
    CONSPIRACIST = "Conspiracist"
    CULTIST = "Cultist"
    UNKNOWN = "Unknown"


@dataclass
class Rumor:
    """A piece of information spreading through the town."""
    id: str
    content: str
    truth_value: str  # "true", "false", "partial"
    status: str  # "private", "public", "suppressed"
    origin_faction: Optional[str] = None
    affected_factions: List[str] = field(default_factory=list)
    known_by: List[str] = field(default_factory=list)  # List of NPC IDs


@dataclass
class Faction:
    """A group of NPCs with shared ideology."""
    id: str
    name: str
    alignment: FactionAlignment
    description: str
    members: List[str] = field(default_factory=list)
    reputation: int = 0  # Player's reputation with this faction (-100 to 100)


@dataclass
class NPCKnowledge:
    """Information an NPC can share at a trust threshold."""
    topic: str
    trust_required: int
    clue_revealed: Optional[str] = None
    one_time: bool = True
    revealed: bool = False


@dataclass
class NPCSecret:
    """A secret an NPC holds that can be discovered through various means."""
    id: str
    description: str
    revealed_by_trust: Optional[int] = None
    revealed_by_clue: Optional[str] = None
    revealed_by_theory: Optional[str] = None
    revealed: bool = False


class NPC:
    """A non-player character with trust, fear, and relationship mechanics."""

    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.title = data.get("title", "")
        self.description = data.get("description", {"base": ""})
        self.location_id = data.get("location_id")
        self.schedule = data.get("schedule", {})

        # Trust and Fear (0-100 scale, visible to player)
        self.trust = data.get("initial_trust", 50)
        self.fear = data.get("initial_fear", 0)

        # Faction & Loyalty
        self.faction_id = data.get("faction_id")
        self.faction_loyalty = data.get("faction_loyalty", 50)  # 0-100

        # Memory & Beliefs
        self.suspects_integration = data.get("suspects_integration", False)
        self.player_alignment_belief = data.get("player_alignment_belief", "Unknown")
        self.key_memories = data.get("key_memories", [])  # List of strings describing events

        # Trust thresholds for relationship status
        self.trust_thresholds = data.get("trust_thresholds", {
            "hostile": 20,
            "wary": 40,
            "neutral": 50,
            "friendly": 70,
            "trusted": 85
        })

        # Dialogue trees by condition
        self.dialogue_trees = data.get("dialogue_trees", {})

        # Knowledge and secrets
        self.knowledge: List[NPCKnowledge] = []
        for k in data.get("knowledge", []):
            self.knowledge.append(NPCKnowledge(
                topic=k["topic"],
                trust_required=k["trust_required"],
                clue_revealed=k.get("clue_revealed"),
                one_time=k.get("one_time", True)
            ))

        self.secrets: List[NPCSecret] = []
        for s in data.get("secrets", []):
            rb = s.get("revealed_by", {})
            self.secrets.append(NPCSecret(
                id=s["id"],
                description=s["description"],
                revealed_by_trust=rb.get("trust_level"),
                revealed_by_clue=rb.get("clue_presented"),
                revealed_by_theory=rb.get("theory_active")
            ))

        # State flags
        self.flags = data.get("flags", {})
        self.flags.setdefault("alive", True)
        self.flags.setdefault("met", False)

        # Reactions to player actions/flags
        self.reactions = data.get("reactions", {})

        # Critical for certain outcomes
        self.critical_for = data.get("critical_for", [])

        # Visual/style
        self.portrait = data.get("portrait")
        self.voice_style = data.get("voice_style", "")

    def get_relationship_status(self) -> str:
        """Get the current relationship status based on trust level."""
        if self.trust >= self.trust_thresholds.get("trusted", 85):
            return "trusted"
        elif self.trust >= self.trust_thresholds.get("friendly", 70):
            return "friendly"
        elif self.trust >= self.trust_thresholds.get("neutral", 50):
            return "neutral"
        elif self.trust >= self.trust_thresholds.get("wary", 40):
            return "wary"
        else:
            return "hostile"

    def modify_trust(self, amount: int, reason: str = "") -> Tuple[int, str]:
        """
        Modify trust level. Returns (new_trust, status_change_message).
        Trust changes are permanent and consequential.
        """
        old_status = self.get_relationship_status()
        old_trust = self.trust

        self.trust = max(0, min(100, self.trust + amount))

        new_status = self.get_relationship_status()

        message = ""
        if old_status != new_status:
            if amount > 0:
                message = f"{self.name}'s trust in you has improved. ({old_status} -> {new_status})"
            else:
                message = f"{self.name}'s trust in you has deteriorated. ({old_status} -> {new_status})"

        # Add memory of significant trust shifts
        if abs(amount) >= 10:
            sentiment = "positive" if amount > 0 else "negative"
            self.add_memory(f"Trust shift ({sentiment}): {reason}")

        return self.trust, message

    def modify_fear(self, amount: int, reason: str = "") -> int:
        """Modify fear level. Fear affects dialogue options and NPC behavior."""
        self.fear = max(0, min(100, self.fear + amount))
        if amount > 10:
             self.add_memory(f"Became afraid: {reason}")
        return self.fear

    def add_memory(self, memory: str):
        """Add a key memory to the NPC."""
        if memory not in self.key_memories:
            self.key_memories.append(memory)

    def get_available_knowledge(self) -> List[NPCKnowledge]:
        """Get knowledge that can be shared based on current trust."""
        available = []
        for k in self.knowledge:
            if not k.revealed and self.trust >= k.trust_required:
                available.append(k)
        return available

    def reveal_knowledge(self, topic: str) -> Optional[str]:
        """
        Reveal knowledge on a topic if trust is sufficient.
        Returns clue_id if a clue is revealed.
        """
        for k in self.knowledge:
            if k.topic == topic and not k.revealed and self.trust >= k.trust_required:
                if k.one_time:
                    k.revealed = True
                return k.clue_revealed
        return None

    def check_secrets(self, player_trust: int = None, clues_presented: List[str] = None,
                      active_theories: List[str] = None) -> List[NPCSecret]:
        """Check if any secrets can be revealed based on current conditions."""
        trust = player_trust if player_trust is not None else self.trust
        clues = clues_presented or []
        theories = active_theories or []

        revealed = []
        for s in self.secrets:
            if s.revealed:
                continue

            can_reveal = False

            if s.revealed_by_trust and trust >= s.revealed_by_trust:
                can_reveal = True
            if s.revealed_by_clue and s.revealed_by_clue in clues:
                can_reveal = True
            if s.revealed_by_theory and s.revealed_by_theory in theories:
                can_reveal = True

            if can_reveal:
                s.revealed = True
                revealed.append(s)

        return revealed

    def get_dialogue_tree_id(self) -> str:
        """Get the appropriate dialogue tree based on relationship status."""
        status = self.get_relationship_status()

        # Check for specific status dialogue
        if status in self.dialogue_trees:
            return self.dialogue_trees[status]

        # Check for default
        if "default" in self.dialogue_trees:
            return self.dialogue_trees["default"]

        return f"dialogue_{self.id}_default"

    def apply_reaction(self, trigger: str) -> dict:
        """
        Apply a reaction based on a trigger (player action/flag).
        Returns dict with changes applied.
        """
        if trigger not in self.reactions:
            return {}

        reaction = self.reactions[trigger]
        result = {"trigger": trigger}

        if "trust_modifier" in reaction:
            self.modify_trust(reaction["trust_modifier"], trigger)
            result["trust_change"] = reaction["trust_modifier"]

        if "fear_modifier" in reaction:
            self.modify_fear(reaction["fear_modifier"], trigger)
            result["fear_change"] = reaction["fear_modifier"]

        if "becomes_unavailable" in reaction and reaction["becomes_unavailable"]:
            self.flags["available"] = False
            result["became_unavailable"] = True

        if "dialogue_override" in reaction:
            result["dialogue_override"] = reaction["dialogue_override"]

        return result

    def is_available(self, current_time_block: str = None, current_location: str = None) -> bool:
        """Check if NPC is available for interaction."""
        if not self.flags.get("alive", True):
            return False
        if self.flags.get("available") is False:
            return False

        # Check schedule if provided
        if current_time_block and self.schedule:
            schedule_entry = self.schedule.get(current_time_block)
            if schedule_entry:
                if not schedule_entry.get("available", True):
                    return False
                if current_location and schedule_entry.get("location") != current_location:
                    return False

        return True

    def get_description(self, lens: str = "neutral") -> str:
        """Get NPC description for current lens."""
        if isinstance(self.description, dict):
            if lens in self.description.get("lens", {}):
                return self.description["lens"][lens]
            return self.description.get("base", "")
        return str(self.description)

    def to_dict(self) -> dict:
        """Serialize NPC state for saving."""
        return {
            "id": self.id,
            "trust": self.trust,
            "fear": self.fear,
            "faction_id": self.faction_id,
            "faction_loyalty": self.faction_loyalty,
            "suspects_integration": self.suspects_integration,
            "player_alignment_belief": self.player_alignment_belief,
            "key_memories": self.key_memories,
            "flags": self.flags,
            "knowledge_revealed": [k.topic for k in self.knowledge if k.revealed],
            "secrets_revealed": [s.id for s in self.secrets if s.revealed]
        }

    @staticmethod
    def restore_state(npc: 'NPC', state: dict):
        """Restore NPC state from saved data."""
        npc.trust = state.get("trust", npc.trust)
        npc.fear = state.get("fear", npc.fear)
        npc.faction_id = state.get("faction_id", npc.faction_id)
        npc.faction_loyalty = state.get("faction_loyalty", npc.faction_loyalty)
        npc.suspects_integration = state.get("suspects_integration", npc.suspects_integration)
        npc.player_alignment_belief = state.get("player_alignment_belief", npc.player_alignment_belief)
        npc.key_memories = state.get("key_memories", npc.key_memories)
        npc.flags = state.get("flags", npc.flags)

        for topic in state.get("knowledge_revealed", []):
            for k in npc.knowledge:
                if k.topic == topic:
                    k.revealed = True

        for secret_id in state.get("secrets_revealed", []):
            for s in npc.secrets:
                if s.id == secret_id:
                    s.revealed = True


class NPCSystem:
    """Manages all NPCs and their relationships with the player."""

    def __init__(self, npcs_dir: str = None):
        self.npcs: Dict[str, NPC] = {}
        self.factions: Dict[str, Faction] = {}
        self.rumors: Dict[str, Rumor] = {}
        self.npcs_dir = npcs_dir

        self._initialize_factions()

        if npcs_dir:
            self.load_npcs(npcs_dir)

    def _initialize_factions(self):
        """Initialize the core factions of Kaltvik."""
        self.factions = {
            "elders": Faction("elders", "Town Elders", FactionAlignment.TRADITIONALIST, "Protective of tradition, suspicious of outsiders."),
            "scientists": Faction("scientists", "Scientists", FactionAlignment.RATIONALIST, "Empirical, data-driven, skeptical."),
            "sheriff": Faction("sheriff", "Sheriff's Office", FactionAlignment.PRAGMATIC, "Pragmatic lawkeepers."),
            "believers": Faction("believers", "Believers", FactionAlignment.CONSPIRACIST, "Seek hidden patterns, often unhinged."),
            "cult": Faction("cult", "Church of Ice", FactionAlignment.CULTIST, "Secretive, view aurora as divine.")
        }

    def load_npcs(self, npcs_dir: str):
        """Load NPC definitions from a directory."""
        if not os.path.exists(npcs_dir):
            return

        for filename in os.listdir(npcs_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(npcs_dir, filename), 'r') as f:
                        data = json.load(f)

                    # Handle array or single object
                    npcs = data if isinstance(data, list) else [data]
                    for npc_data in npcs:
                        npc = NPC(npc_data)
                        self.npcs[npc.id] = npc

                        # Register with faction if set
                        if npc.faction_id and npc.faction_id in self.factions:
                            self.factions[npc.faction_id].members.append(npc.id)

                except Exception as e:
                    print(f"Error loading NPC from {filename}: {e}")

    def load_npc(self, npc_data: dict) -> NPC:
        """Load a single NPC from data."""
        npc = NPC(npc_data)
        self.npcs[npc.id] = npc
        if npc.faction_id and npc.faction_id in self.factions:
             self.factions[npc.faction_id].members.append(npc.id)
        return npc

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Get an NPC by ID."""
        return self.npcs.get(npc_id)

    def get_npcs_at_location(self, location_id: str, time_block: str = None) -> List[NPC]:
        """Get all available NPCs at a location."""
        result = []
        for npc in self.npcs.values():
            if npc.is_available(time_block, location_id):
                # Check if NPC is at this location
                if npc.location_id == location_id:
                    result.append(npc)
                elif time_block and npc.schedule:
                    schedule = npc.schedule.get(time_block, {})
                    if schedule.get("location") == location_id:
                        result.append(npc)
        return result

    def get_trust_summary(self) -> Dict[str, dict]:
        """Get a summary of trust levels with all NPCs."""
        summary = {}
        for npc_id, npc in self.npcs.items():
            if npc.flags.get("met", False):
                summary[npc_id] = {
                    "name": npc.name,
                    "trust": npc.trust,
                    "fear": npc.fear,
                    "status": npc.get_relationship_status(),
                    "alive": npc.flags.get("alive", True),
                    "faction": npc.faction_id
                }
        return summary

    def modify_trust(self, npc_id: str, amount: int, reason: str = "") -> Optional[Tuple[int, str]]:
        """Modify trust for a specific NPC."""
        npc = self.get_npc(npc_id)
        if npc:
            return npc.modify_trust(amount, reason)
        return None

    def modify_faction_reputation(self, faction_id: str, amount: int):
        """Modify reputation with an entire faction."""
        if faction_id in self.factions:
            self.factions[faction_id].reputation = max(-100, min(100, self.factions[faction_id].reputation + amount))

            # Ripple effect to members
            for npc_id in self.factions[faction_id].members:
                npc = self.get_npc(npc_id)
                if npc:
                    # Impact depends on loyalty
                    impact = int(amount * (npc.faction_loyalty / 100.0))
                    if impact != 0:
                        npc.modify_trust(impact, f"Faction reputation change ({faction_id})")

    def create_rumor(self, id: str, content: str, truth_value: str, status: str, origin_faction: str = None) -> Rumor:
        """Create and track a new rumor."""
        rumor = Rumor(id, content, truth_value, status, origin_faction)
        self.rumors[id] = rumor
        return rumor

    def spread_rumor(self, rumor_id: str, target_faction: str = None):
        """Spread an existing rumor to a faction or publicly."""
        if rumor_id not in self.rumors:
            return

        rumor = self.rumors[rumor_id]

        if target_faction:
            if target_faction in self.factions and target_faction not in rumor.affected_factions:
                rumor.affected_factions.append(target_faction)
                # Faction members learn it
                for member_id in self.factions[target_faction].members:
                    if member_id not in rumor.known_by:
                        rumor.known_by.append(member_id)
        else:
            # Spread to everyone (Public)
            rumor.status = "public"
            for npc in self.npcs.values():
                if npc.id not in rumor.known_by:
                    rumor.known_by.append(npc.id)

    def apply_global_reaction(self, trigger: str) -> Dict[str, dict]:
        """Apply a reaction trigger to all NPCs, returning results."""
        results = {}
        for npc_id, npc in self.npcs.items():
            result = npc.apply_reaction(trigger)
            if result:
                results[npc_id] = result
        return results

    def get_board_nodes(self) -> List[dict]:
        """Get NPC data formatted for the Board system."""
        nodes = []
        for npc in self.npcs.values():
            if npc.flags.get("met", False):
                nodes.append({
                    "id": npc.id,
                    "type": "npc",
                    "title": npc.name,
                    "summary": npc.title or npc.get_relationship_status(),
                    "tags": [npc.get_relationship_status(), "npc"],
                    "trust": npc.trust,
                    "fear": npc.fear
                })
        return nodes

    def to_dict(self) -> dict:
        """Serialize all NPC states for saving."""
        return {
            "npcs": {npc_id: npc.to_dict() for npc_id, npc in self.npcs.items()},
            "factions": {
                fid: {
                    "reputation": f.reputation,
                    "members": f.members
                } for fid, f in self.factions.items()
            },
            "rumors": {
                rid: {
                    "content": r.content,
                    "truth": r.truth_value,
                    "status": r.status,
                    "known_by": r.known_by,
                    "affected": r.affected_factions
                } for rid, r in self.rumors.items()
            }
        }

    def restore_states(self, states: dict):
        """Restore NPC states from saved data."""
        # Handle old save format (just dict of NPCs) vs new format (nested)
        if "npcs" in states:
            npc_states = states["npcs"]
            faction_states = states.get("factions", {})
            rumor_states = states.get("rumors", {})
        else:
            npc_states = states
            faction_states = {}
            rumor_states = {}

        for npc_id, state in npc_states.items():
            npc = self.get_npc(npc_id)
            if npc:
                NPC.restore_state(npc, state)

        # Restore faction reputation
        for fid, f_data in faction_states.items():
            if fid in self.factions:
                self.factions[fid].reputation = f_data.get("reputation", 0)

        # Restore rumors
        self.rumors = {}
        for rid, r_data in rumor_states.items():
            self.rumors[rid] = Rumor(
                id=rid,
                content=r_data["content"],
                truth_value=r_data["truth"],
                status=r_data["status"],
                known_by=r_data["known_by"],
                affected_factions=r_data["affected"]
            )


# Example NPC data for testing
EXAMPLE_NPC_DATA = {
    "id": "npc_sheriff_bergman",
    "name": "Sheriff Bergman",
    "title": "Local Sheriff",
    "faction_id": "sheriff",
    "faction_loyalty": 90,
    "description": {
        "base": "A weathered man in his fifties with tired eyes and a permanent frown.",
        "lens": {
            "believer": "His eyes dart nervously, as if he's seen things he can't explain.",
            "skeptic": "A pragmatic lawman worn down by isolation and limited resources.",
            "haunted": "He reminds you of someone. The resemblance is unsettling."
        }
    },
    "location_id": "loc_sheriff_office",
    "initial_trust": 40,
    "initial_fear": 0,
    "knowledge": [
        {
            "topic": "recent_disappearances",
            "trust_required": 50,
            "clue_revealed": "clue_case_files",
            "one_time": True
        },
        {
            "topic": "aurora_sightings",
            "trust_required": 70,
            "clue_revealed": "clue_aurora_reports",
            "one_time": True
        }
    ],
    "secrets": [
        {
            "id": "secret_bergman_knows",
            "description": "The Sheriff knows more about the disappearances than he admits.",
            "revealed_by": {
                "trust_level": 85,
                "theory_active": "government_coverup"
            }
        }
    ],
    "dialogue_trees": {
        "hostile": "dialogue_bergman_hostile",
        "wary": "dialogue_bergman_wary",
        "neutral": "dialogue_bergman_neutral",
        "friendly": "dialogue_bergman_friendly",
        "trusted": "dialogue_bergman_trusted"
    },
    "reactions": {
        "accused_sheriff": {
            "trust_modifier": -20,
            "dialogue_override": "dialogue_bergman_accused"
        },
        "saved_deputy": {
            "trust_modifier": 25
        }
    }
}


if __name__ == "__main__":
    # Test NPC system
    system = NPCSystem()
    npc = system.load_npc(EXAMPLE_NPC_DATA)

    print(f"NPC: {npc.name}")
    print(f"Trust: {npc.trust}")
    print(f"Faction: {npc.faction_id}")
    print(f"Loyalty: {npc.faction_loyalty}")

    # Test trust modification
    new_trust, msg = npc.modify_trust(15, "helped investigation")
    print(f"After +15: {new_trust} - {msg}")

    # Test Faction Ripple
    print("\nTesting Faction Reputation change...")
    system.modify_faction_reputation("sheriff", -50)
    print(f"Faction Reputation: {system.factions['sheriff'].reputation}")
    print(f"NPC Trust after faction hit: {npc.trust}")

    # Check available knowledge
    print(f"Available knowledge: {[k.topic for k in npc.get_available_knowledge()]}")

    # Test serialization
    state = system.to_dict()
    # print(f"Saved state: {state}")
