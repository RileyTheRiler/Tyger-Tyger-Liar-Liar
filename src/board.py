from typing import Dict, List, Optional
from theories import THEORY_DATA

class Theory:
    def __init__(self, id_key: str, data: dict):
        self.id = id_key
        self.name = data["name"]
        self.category = data["category"]
        self.description = data["description"]
        self.hidden_effects = data.get("hidden_effects", False)
        self.effects = data.get("effects", {})
        self.conflicts_with = data.get("conflicts_with", [])
        self.internalize_time_hours = data.get("internalize_time_hours", 4)
        self.active_case = data.get("active_case", False)
        self.critical_for_endgame = data.get("critical_for_endgame", False)
        
        # State
        self.status = "available" # active, internalizing, available, locked
        self.internalization_progress_minutes = 0
        
        # Resolution tracking (for endgame)
        self.proven: Optional[bool] = None  # None = unresolved, True = proven, False = disproven
        self.evidence_count: int = 0  # Supporting evidence
        self.contradictions: int = 0  # Contradicting evidence
        self.linked_evidence: List[str] = []  # Evidence IDs

class Board:
    def __init__(self):
        self.max_slots = 3
        self.theories: Dict[str, Theory] = {}
        self._load_theories()
        
    def _load_theories(self):
        for key, data in THEORY_DATA.items():
            self.theories[key] = Theory(key, data)

    def get_theory(self, theory_id: str) -> Optional[Theory]:
        return self.theories.get(theory_id)

    def start_internalizing(self, theory_id: str) -> bool:
        theory = self.get_theory(theory_id)
        if not theory:
            return False
            
        if self.get_active_or_internalizing_count() >= self.max_slots:
            return False
            
        # Check conflicts
        for other_id, other_t in self.theories.items():
            if other_t.status == "active" and (other_id in theory.conflicts_with or theory_id in other_t.conflicts_with):
                return False

        theory.status = "internalizing"
        theory.internalization_progress_minutes = 0
        return True

    def on_time_passed(self, minutes: int) -> List[str]:
        messages = []
        for theory in self.theories.values():
            if theory.status == "internalizing":
                theory.internalization_progress_minutes += minutes
                required_minutes = theory.internalize_time_hours * 60
                
                if theory.internalization_progress_minutes >= required_minutes:
                    theory.status = "active"
                    messages.append(f"Theory Internalized: '{theory.name}'")
                    
        return messages

    def get_all_modifiers(self) -> Dict[str, int]:
        combined_effects = {}
        for theory in self.theories.values():
            if theory.status == "active":
                for skill, val in theory.effects.items():
                    combined_effects[skill] = combined_effects.get(skill, 0) + val
            # Optionally: internalizing theories might have partial or different effects? 
            # For now, only active ones apply.
        return combined_effects
        
    def get_active_or_internalizing_count(self) -> int:
        count = 0
        for t in self.theories.values():
            if t.status in ["active", "internalizing"]:
                count += 1
        return count

    def discover_theory(self, theory_id: str) -> bool:
        """Unlocks a theory, making it available for internalization."""
        theory = self.get_theory(theory_id)
        if not theory:
            return False
        if theory.status == "locked":
            theory.status = "available"
            return True
        return False

    def is_theory_active(self, theory_id: str) -> bool:
        """Check if a theory is currently active."""
        theory = self.get_theory(theory_id)
        return theory and theory.status == "active"

    def resolve_theory(self, theory_id: str, is_proven: bool) -> bool:
        """Mark a theory as proven or disproven."""
        theory = self.get_theory(theory_id)
        if not theory:
            return False
        
        theory.proven = is_proven
        print(f"[BOARD] Theory '{theory.name}' marked as {'PROVEN' if is_proven else 'DISPROVEN'}")
        return True

    def add_evidence_to_theory(self, theory_id: str, evidence_id: str) -> bool:
        """Link supporting evidence to a theory."""
        theory = self.get_theory(theory_id)
        if not theory:
            return False
        
        if evidence_id not in theory.linked_evidence:
            theory.linked_evidence.append(evidence_id)
            theory.evidence_count += 1
            print(f"[BOARD] Evidence linked to '{theory.name}' ({theory.evidence_count} total)")
            return True
        return False

    def add_contradiction_to_theory(self, theory_id: str, evidence_id: str) -> bool:
        """Link contradicting evidence to a theory."""
        theory = self.get_theory(theory_id)
        if not theory:
            return False
        
        if evidence_id not in theory.linked_evidence:
            theory.linked_evidence.append(evidence_id)
            theory.contradictions += 1
            print(f"[BOARD] Contradiction found for '{theory.name}' ({theory.contradictions} total)")
            return True
        return False

    def get_resolution_summary(self) -> Dict[str, int]:
        """Get counts of proven/disproven/unresolved theories."""
        proven = 0
        disproven = 0
        unresolved = 0
        
        for theory in self.theories.values():
            if theory.status == "active":
                if theory.proven is True:
                    proven += 1
                elif theory.proven is False:
                    disproven += 1
                else:
                    unresolved += 1
        
        return {
            "proven": proven,
            "disproven": disproven,
            "unresolved": unresolved
        }

    def get_critical_theories(self) -> List[str]:
        """Get list of theories marked as critical for endgame."""
        critical = []
        for theory_id, theory in self.theories.items():
            if theory.critical_for_endgame:
                critical.append(theory_id)
        return critical

    def get_proven_theories(self) -> List[str]:
        """Get list of proven theory names."""
        proven = []
        for theory in self.theories.values():
            if theory.proven is True:
                proven.append(theory.name)
        return proven
