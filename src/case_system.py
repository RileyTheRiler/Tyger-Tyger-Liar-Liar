from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import json

class OutcomeType(Enum):
    ACCURATE = "Solved Accurately"
    PARTIAL = "Partial Closure"
    FALSE = "False Solution"

@dataclass
class Outcome:
    id: str
    type: OutcomeType
    description: str
    required_theory: str  # The theory that must be active/selected
    required_clues: List[str]  # Clues that must have been found (optional extra check)
    consequences: dict  # Effects on trust, flags, factions
    narrative_text: str # Text to display upon resolution

@dataclass
class Case:
    id: str
    title: str
    hook: str
    description: str
    clues: List[str]  # IDs of clues belonging to this case
    theories: List[str] # IDs of theories relevant to this case
    outcomes: List[Outcome]
    active: bool = False
    solved: bool = False
    resolution: Optional[str] = None # ID of the outcome achieved

class CaseSystem:
    def __init__(self, board=None, clue_system=None, journal_system=None, cases_dir=None):
        self.cases: Dict[str, Case] = {}
        self.active_case_id: Optional[str] = None
        self.board = board
        self.clue_system = clue_system
        self.journal_system = journal_system

        # Default directory relative to execution
        import os, sys
        def resource_path(relative_path):
             try:
                 base_path = sys._MEIPASS
             except Exception:
                 base_path = os.path.abspath(".")
             return os.path.join(base_path, relative_path)

        self.cases_dir = cases_dir or resource_path(os.path.join('data', 'cases'))
        self._load_cases()

    def _load_cases(self):
        import os
        if not os.path.exists(self.cases_dir):
            print(f"[CASE SYSTEM] Warning: Cases directory not found at {self.cases_dir}")
            return

        for filename in os.listdir(self.cases_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.cases_dir, filename), 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for case_data in data:
                                self._load_single_case(case_data)
                        else:
                             self._load_single_case(data)
                except Exception as e:
                    print(f"[CASE SYSTEM] Error loading case {filename}: {e}")

    def _load_single_case(self, data: dict):
        outcomes = []
        for out_data in data.get("outcomes", []):
            try:
                out_type = OutcomeType[out_data["type"]] # Expecting string like "FALSE" or "ACCURATE"
            except KeyError:
                # Fallback or error
                out_type = OutcomeType.PARTIAL

            outcomes.append(Outcome(
                id=out_data["id"],
                type=out_type,
                description=out_data["description"],
                required_theory=out_data["required_theory"],
                required_clues=out_data.get("required_clues", []),
                consequences=out_data.get("consequences", {}),
                narrative_text=out_data.get("narrative_text", "")
            ))

        case = Case(
            id=data["id"],
            title=data["title"],
            hook=data["hook"],
            description=data["description"],
            clues=data.get("clues", []),
            theories=data.get("theories", []),
            outcomes=outcomes
        )
        self.cases[case.id] = case
        print(f"[CASE SYSTEM] Loaded case: {case.title}")

    def start_case(self, case_id: str):
        if case_id in self.cases:
            self.active_case_id = case_id
            self.cases[case_id].active = True
            print(f"[CASE] Started case: {self.cases[case_id].title}")

            # Log to journal
            if self.journal_system:
                self.journal_system.add_entry(
                    title=f"CASE OPENED: {self.cases[case_id].title}",
                    body=self.cases[case_id].hook,
                    tags=["case", "investigation"]
                )

            # Add clues to board if they are already found?
            # Usually clues are found during gameplay.
        else:
            print(f"[CASE] Error: Case {case_id} not found.")

    def get_active_case(self) -> Optional[Case]:
        if self.active_case_id:
            return self.cases.get(self.active_case_id)
        return None

    def resolve_case(self, theory_id: str) -> dict:
        """
        Attempt to resolve the active case using the provided theory.
        """
        case = self.get_active_case()
        if not case:
            return {"success": False, "message": "No active case."}

        # Check if theory is valid for this case
        if theory_id not in case.theories:
             return {"success": False, "message": "This theory does not apply to the current case."}

        # Find matching outcome
        selected_outcome = None
        for outcome in case.outcomes:
            if outcome.required_theory == theory_id:
                # Check additional constraints (e.g. required clues)
                missing_clues = []
                if self.clue_system:
                    for clue_id in outcome.required_clues:
                        if not self.clue_system.has_clue(clue_id):
                            missing_clues.append(clue_id)

                if not missing_clues:
                    selected_outcome = outcome
                    break

        if selected_outcome:
            case.solved = True
            case.resolution = selected_outcome.id
            case.active = False
            self.active_case_id = None

            # Log resolution
            print(f"[CASE] Case Resolved: {selected_outcome.type.value}")
            if self.journal_system:
                self.journal_system.add_entry(
                    title=f"CASE CLOSED: {case.title}",
                    body=f"CONCLUSION: {selected_outcome.description}\n\n{selected_outcome.narrative_text}",
                    tags=["case", "resolution", selected_outcome.type.name]
                )

            return {
                "success": True,
                "outcome": selected_outcome,
                "message": selected_outcome.narrative_text
            }
        else:
            # Fallback for "Theory matched but evidence missing" or "Theory not a valid solution"
            # In a real game we might allow submitting a wrong theory that isn't even in the outcome list
            # and treating it as a generic failure.
            return {"success": False, "message": "You lack the evidence to prove this theory, or it leads nowhere."}

    def get_case_status(self) -> dict:
        case = self.get_active_case()
        if not case:
            return {"active": False}

        return {
            "active": True,
            "id": case.id,
            "title": case.title,
            "hook": case.hook,
            "clues_found_count": 0, # TODO link to ClueSystem
            "theories_available": case.theories
        }

    def to_dict(self) -> dict:
        """Serialize case system state."""
        cases_data = {}
        for case_id, case in self.cases.items():
            cases_data[case_id] = {
                "active": case.active,
                "solved": case.solved,
                "resolution": case.resolution
            }

        return {
            "active_case_id": self.active_case_id,
            "cases": cases_data
        }

    def restore_state(self, state: dict):
        """Restore case system state."""
        self.active_case_id = state.get("active_case_id")

        cases_data = state.get("cases", {})
        for case_id, case_state in cases_data.items():
            if case_id in self.cases:
                self.cases[case_id].active = case_state.get("active", False)
                self.cases[case_id].solved = case_state.get("solved", False)
                self.cases[case_id].resolution = case_state.get("resolution")
