import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class JournalEntry:
    """Narrative or discovery log entry."""
    id: str
    timestamp: str
    title: str
    what_happened: str
    meaning: str
    confidence: str # "Low", "Medium", "High"
    tags: List[str] = field(default_factory=list)
    context: Dict = field(default_factory=dict) # To allow retroactive updates based on state

@dataclass
class Suspect:
    id: str
    name: str
    age: int
    role: str
    notes: str
    status: str = "Active"  # Options: Cleared, Active, Missing, Deceased, Arrested
    evidence_links: List[str] = field(default_factory=list)
    theory_links: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)  # e.g., "Deceptive", "Dangerous"

@dataclass
class TimelineEvent:
    datetime_str: str  # ISO format preferred
    title: str
    details: str
    tags: List[str] = field(default_factory=list)
    source: str = "Player Discovery"

@dataclass
class OpenQuestion:
    id: str
    question: str
    source: str
    status: str = "Open"  # Open, Partially Answered, Resolved
    linked_evidence: List[str] = field(default_factory=list)
    linked_suspects: List[str] = field(default_factory=list)
    linked_theories: List[str] = field(default_factory=list)

@dataclass
class Annotation:
    target_id: str  # ID of scene, evidence, person, etc.
    text: str
    timestamp: str

class JournalManager:
    def __init__(self):
        self.entries: List[JournalEntry] = []  # Week 6: Narrative entries
        self.suspects: Dict[str, Suspect] = {}
        self.timeline: List[TimelineEvent] = []
        self.questions: Dict[str, OpenQuestion] = {}
        self.annotations: List[Annotation] = []
        self.leads: List[str] = []  # Week 6: Open threads/mystery flags

    def add_entry(self, title: str, what_happened: str, meaning: str = "Unclear significance.", confidence: str = "Low", tags: List[str] = None, timestamp: str = None, context: Dict = None):
        """Add a narrative journal entry."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        entry_id = str(uuid.uuid4())[:8]
        entry = JournalEntry(
            id=entry_id,
            timestamp=timestamp,
            title=title,
            what_happened=what_happened,
            meaning=meaning,
            confidence=confidence,
            tags=tags or [],
            context=context or {}
        )
        self.entries.append(entry)
        # print(f"[Journal] Entry added: {title}")
        return entry_id

    def update_entry(self, entry_id: str, meaning: str = None, confidence: str = None):
        """Retroactively update an entry's meaning or confidence."""
        for entry in self.entries:
            if entry.id == entry_id:
                if meaning:
                    entry.meaning = meaning
                if confidence:
                    entry.confidence = confidence
                # print(f"[Journal] Entry updated: {entry.title}")
                return True
        return False

    def add_suspect(self, suspect_data: dict):
        """Adds or updates a suspect entry."""
        if "evidence_links" not in suspect_data:
            suspect_data["evidence_links"] = []
        if "theory_links" not in suspect_data:
            suspect_data["theory_links"] = []
        if "flags" not in suspect_data:
            suspect_data["flags"] = []
            
        suspect = Suspect(**suspect_data)
        self.suspects[suspect.id] = suspect
        print(f"[Journal] Suspect added/updated: {suspect.name}")

    def update_suspect_status(self, suspect_id: str, new_status: str):
        if suspect_id in self.suspects:
            self.suspects[suspect_id].status = new_status
            print(f"[Journal] Updated {self.suspects[suspect_id].name} status to {new_status}")
    
    def add_suspect_flag(self, suspect_id: str, flag: str):
        if suspect_id in self.suspects:
            if flag not in self.suspects[suspect_id].flags:
                self.suspects[suspect_id].flags.append(flag)

    def add_timeline_event(self, event_data: dict):
        """Adds a timeline event."""
        if "tags" not in event_data:
            event_data["tags"] = []
        event = TimelineEvent(**event_data)
        self.timeline.append(event)
        # Sort by datetime
        self.timeline.sort(key=lambda x: x.datetime_str)
        print(f"[Journal] Timeline event added: {event.title}")

    def get_timeline(self, tag_filter: Optional[str] = None, source_filter: Optional[str] = None) -> List[TimelineEvent]:
        results = self.timeline
        if tag_filter:
            results = [e for e in results if tag_filter in e.tags]
        if source_filter:
            results = [e for e in results if e.source == source_filter]
        return results

    def add_question(self, question_data: dict):
        """Adds an open question."""
        if "linked_evidence" not in question_data:
             question_data["linked_evidence"] = []
        if "linked_suspects" not in question_data:
             question_data["linked_suspects"] = []
        if "linked_theories" not in question_data:
             question_data["linked_theories"] = []

        q = OpenQuestion(**question_data)
        self.questions[q.id] = q
        print(f"[Journal] New Question: {q.question}")

    def resolve_question(self, question_id: str):
        if question_id in self.questions:
            self.questions[question_id].status = "Resolved"
            print(f"[Journal] Question resolved: {self.questions[question_id].question}")

    def add_annotation(self, target_id: str, text: str):
        """Adds a player note."""
        timestamp = datetime.now().isoformat()
        note = Annotation(target_id=target_id, text=text, timestamp=timestamp)
        self.annotations.append(note)
        print(f"[Journal] Note added for {target_id}")

    def link_evidence_to_suspect(self, suspect_id: str, evidence_id: str):
        if suspect_id in self.suspects:
            if evidence_id not in self.suspects[suspect_id].evidence_links:
                self.suspects[suspect_id].evidence_links.append(evidence_id)
                print(f"[Journal] Linked evidence {evidence_id} to {suspect_id}")
    
    def add_lead(self, lead: str):
        """Add an open thread or mystery flag."""
        if lead not in self.leads:
            self.leads.append(lead)
            print(f"[Journal] New lead: {lead}")
    
    def display_journal(self, limit: int = 5):
        """Display recent journal entries with new UI."""
        from ui.interface import Colors

        print("\n" + "="*60)
        print(f"{Colors.BOLD}CASE FILE / JOURNAL{Colors.RESET}")
        print("="*60)
        
        if not self.entries:
            print(" (No entries)")
            return
        
        recent = self.entries[-limit:]
        for entry in reversed(recent):
            print(f"\n{Colors.CYAN}REF: {entry.id} | {entry.timestamp}{Colors.RESET}")
            print(f"{Colors.BOLD}EVENT:{Colors.RESET} {entry.what_happened}")

            # Color code confidence
            conf_color = Colors.RED
            if entry.confidence.lower() == "medium": conf_color = Colors.YELLOW
            elif entry.confidence.lower() == "high": conf_color = Colors.GREEN

            print(f"{Colors.BOLD}INTERPRETATION:{Colors.RESET} {entry.meaning}")
            print(f"{Colors.BOLD}CONFIDENCE:{Colors.RESET} {conf_color}{entry.confidence.upper()}{Colors.RESET}")

            if entry.tags:
                print(f"{Colors.GREY}Tags: {', '.join(entry.tags)}{Colors.RESET}")
            print("-" * 60)

    def export_state(self) -> dict:
        return {
            "entries": [asdict(e) for e in self.entries],
            "suspects": {k: asdict(v) for k, v in self.suspects.items()},
            "timeline": [asdict(e) for e in self.timeline],
            "questions": {k: asdict(v) for k, v in self.questions.items()},
            "annotations": [asdict(a) for a in self.annotations],
            "leads": self.leads
        }

    def load_state(self, data: dict):
        self.entries = [JournalEntry(**v) for v in data.get("entries", [])]
        self.suspects = {k: Suspect(**v) for k, v in data.get("suspects", {}).items()}
        self.timeline = [TimelineEvent(**v) for v in data.get("timeline", [])]
        self.questions = {k: OpenQuestion(**v) for k, v in data.get("questions", {}).items()}
        self.annotations = [Annotation(**v) for v in data.get("annotations", [])]
        self.leads = data.get("leads", [])
