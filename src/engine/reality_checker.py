"""
Reality Consistency Checker - Dev Tool
Tracks narrative consistency and flags contradictions between asserted facts and game state.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import time

@dataclass
class RealityFact:
    """A single asserted fact about the game world."""
    subject: str          # e.g., "npc_alice", "weather", "player"
    attribute: str        # e.g., "location", "status", "has_item"
    value: Any           # e.g., "hotel_lobby", "dead", True
    timestamp: int        # Game time in minutes
    location_id: str      # ID of the location where this fact was asserted
    is_distorted: bool    # Whether this fact came from a distorted source (hallucination, lens)
    source_text: str      # The text snippet that established this fact
    real_time: float = field(default_factory=time.time)

@dataclass
class Contradiction:
    """A detected inconsistency."""
    fact_new: RealityFact
    fact_old: RealityFact
    message: str
    severity: str = "WARNING"

class RealityConsistencyChecker:
    def __init__(self, debug_mode: bool = False):
        self.facts: List[RealityFact] = []
        self.debug_mode = debug_mode
        self.contradictions: List[Contradiction] = []
        self.ignored_subjects = set(["weather"]) # Things that change naturally and often

    def register_fact(self,
                      subject: str,
                      attribute: str,
                      value: Any,
                      timestamp: int,
                      location_id: str,
                      is_distorted: bool,
                      source_text: str):
        """
        Register a new fact and check for contradictions.
        """
        new_fact = RealityFact(
            subject=subject,
            attribute=attribute,
            value=value,
            timestamp=timestamp,
            location_id=location_id,
            is_distorted=is_distorted,
            source_text=source_text
        )

        # If the new fact is distorted, we don't treat it as "Truth", but we log it.
        # Contradictions *caused* by distorted facts are ignored (or flagged as 'Hallucination Mismatch').

        self._check_consistency(new_fact)
        self.facts.append(new_fact)

    def _check_consistency(self, new_fact: RealityFact):
        """
        Compare the new fact against history.
        """
        if new_fact.subject in self.ignored_subjects:
            return

        # We search for facts with same Subject and Attribute
        related_facts = [f for f in self.facts if f.subject == new_fact.subject and f.attribute == new_fact.attribute]

        for old_fact in related_facts:
            # Case 1: Same Time, Different Value -> Direct Contradiction
            # We treat facts as valid for their exact timestamp.
            # Narrative consistency usually implies that at time T, X cannot be both True and False.
            time_diff = abs(new_fact.timestamp - old_fact.timestamp)

            # Strict simultaneity for location to allow movement (which advances time)
            threshold = 0 if new_fact.attribute == "location" else 2

            if time_diff <= threshold:
                if new_fact.value != old_fact.value:
                    self._flag_contradiction(new_fact, old_fact, "Simultaneous conflicting facts")

            # Case 2: Retroactive Continuity Error?
            # If new_fact is in the PAST relative to old_fact?
            if new_fact.timestamp < old_fact.timestamp:
                 # This might be a flashback, or a bug.
                 # If it's a flashback, maybe we should ignore?
                 # Assuming linear gameplay for now.
                 pass

    def _flag_contradiction(self, new_fact: RealityFact, old_fact: RealityFact, reason: str):
        """
        Record a contradiction if relevant.
        """
        # If either fact is distorted, it's not a bug, it's a feature (Narrative Dissonance).
        if new_fact.is_distorted or old_fact.is_distorted:
            if self.debug_mode:
                # Log it as info, not warning
                # print(f"[RCC] Dissonance noted: {reason} (Distorted)")
                pass
            return

        msg = f"{reason}: {new_fact.subject}.{new_fact.attribute} = '{new_fact.value}' (New) vs '{old_fact.value}' (Old)"

        c = Contradiction(new_fact, old_fact, msg)
        self.contradictions.append(c)

        if self.debug_mode:
            print(f"\033[31m[REALITY ERROR] {msg}\033[0m")
            print(f"  > Old: {old_fact.source_text[:50]}... (@ {old_fact.timestamp})")
            print(f"  > New: {new_fact.source_text[:50]}... (@ {new_fact.timestamp})")

    def generate_report(self) -> str:
        """
        Generate a summary report of the playthrough.
        """
        lines = ["=== Reality Consistency Report ==="]
        lines.append(f"Total Facts Tracked: {len(self.facts)}")
        lines.append(f"Contradictions Found: {len(self.contradictions)}")
        lines.append("")

        if self.contradictions:
            for c in self.contradictions:
                lines.append(f"[{c.severity}] {c.message}")
                lines.append(f"  Context 1: {c.fact_old.source_text} (Time: {c.fact_old.timestamp}, Loc: {c.fact_old.location_id})")
                lines.append(f"  Context 2: {c.fact_new.source_text} (Time: {c.fact_new.timestamp}, Loc: {c.fact_new.location_id})")
                lines.append("-" * 40)
        else:
            lines.append("No objective contradictions detected.")

        return "\n".join(lines)
