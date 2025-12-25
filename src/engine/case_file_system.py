from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
import json
import os

@dataclass
class Evidence:
    id: str
    name: str
    description: str
    type: str  # Physical, Testimonial, Psychic
    credibility: str  # Clean, Contaminated, Disputed
    linked_case_id: str
    tags: Set[str] = field(default_factory=set)

    def to_dict(self):
        d = asdict(self)
        d['tags'] = list(self.tags)
        return d

    @classmethod
    def from_dict(cls, data):
        data['tags'] = set(data.get('tags', []))
        return cls(**data)

@dataclass
class CaseFile:
    id: str
    title: str
    description: str
    suspects: List[str]  # NPC IDs
    witnesses: List[str] # NPC IDs
    timeline: List[Dict] # {time, event_description}
    evidence_ids: List[str] # All possible evidence for this case
    status: str = "open" # open, closed, archived

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class CaseFileSystem:
    def __init__(self, data_path="data/cases.json"):
        self.cases: Dict[str, CaseFile] = {}
        self.evidence_pool: Dict[str, Evidence] = {}

        # Runtime State
        self.discovered_evidence: Set[str] = set()
        self.discovered_suspects: Dict[str, List[str]] = {} # case_id -> list of npc_ids

        self.data_path = data_path
        self._load_data()

    def _load_data(self):
        # Initial empty load or load from file if exists
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r') as f:
                data = json.load(f)
                for c_data in data.get('cases', []):
                    case = CaseFile.from_dict(c_data)
                    self.cases[case.id] = case
                for e_data in data.get('evidence', []):
                    ev = Evidence.from_dict(e_data)
                    self.evidence_pool[ev.id] = ev

    def save_data(self):
        """Save the static definitions (Editor tool)"""
        data = {
            'cases': [c.to_dict() for c in self.cases.values()],
            'evidence': [e.to_dict() for e in self.evidence_pool.values()]
        }
        with open(self.data_path, 'w') as f:
            json.dump(data, f, indent=2)

    def create_case(self, id: str, title: str, description: str) -> CaseFile:
        if id in self.cases:
            return self.cases[id]

        case = CaseFile(
            id=id,
            title=title,
            description=description,
            suspects=[],
            witnesses=[],
            timeline=[],
            evidence_ids=[]
        )
        self.cases[id] = case
        return case

    def add_evidence(self, evidence: Evidence):
        """Register evidence definition."""
        self.evidence_pool[evidence.id] = evidence
        if evidence.linked_case_id in self.cases:
            case = self.cases[evidence.linked_case_id]
            if evidence.id not in case.evidence_ids:
                case.evidence_ids.append(evidence.id)

    def get_case(self, case_id: str) -> Optional[CaseFile]:
        return self.cases.get(case_id)

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        return self.evidence_pool.get(evidence_id)

    def add_suspect(self, case_id: str, suspect_id: str):
        case = self.get_case(case_id)
        if case and suspect_id not in case.suspects:
            case.suspects.append(suspect_id)

    def add_witness(self, case_id: str, witness_id: str):
        case = self.get_case(case_id)
        if case and witness_id not in case.witnesses:
            case.witnesses.append(witness_id)

    def add_timeline_event(self, case_id: str, time: str, description: str):
        case = self.get_case(case_id)
        if case:
            case.timeline.append({"time": time, "description": description})

    # --- Runtime Progression Methods ---

    def discover_evidence(self, evidence_id: str) -> bool:
        """Mark evidence as discovered by the player."""
        if evidence_id in self.evidence_pool:
            if evidence_id not in self.discovered_evidence:
                self.discovered_evidence.add(evidence_id)
                return True
        return False

    def is_evidence_discovered(self, evidence_id: str) -> bool:
        return evidence_id in self.discovered_evidence

    def discover_suspect(self, case_id: str, suspect_id: str):
        if case_id not in self.cases: return

        if case_id not in self.discovered_suspects:
            self.discovered_suspects[case_id] = []

        if suspect_id not in self.discovered_suspects[case_id]:
            self.discovered_suspects[case_id].append(suspect_id)

    def get_player_case_state(self):
        """Return dict of what the player knows (for save/load)."""
        return {
            "discovered_evidence": list(self.discovered_evidence),
            "discovered_suspects": self.discovered_suspects
        }

    def load_player_case_state(self, data: dict):
        """Restore player progress."""
        self.discovered_evidence = set(data.get("discovered_evidence", []))
        self.discovered_suspects = data.get("discovered_suspects", {})
