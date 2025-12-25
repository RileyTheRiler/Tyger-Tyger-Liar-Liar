import json
from typing import List, Dict, Optional, Any

class Item:
    def __init__(self, id: str, name: str, type: str, description: str, effects: Dict[str, Any] = None, usable_in: List[str] = None, limited_use: bool = False, uses: int = 0):
        self.id = id
        self.name = name
        self.type = type  # tool, key_item, consumable
        self.description = description
        self.effects = effects or {} 
        # effects example: {"action": "take_photo", "modifier": "+1 Forensics"}
        # Wait, the prompt example was: "modifier": "+1 Forensics on visual evidence"
        # We need a structured way to parse modifiers.
        # Simple version: "skill_modifiers": {"Forensics": 1}
        
        self.usable_in = usable_in or []
        self.limited_use = limited_use
        self.uses = uses
        self.temperature = effects.get("temperature", 70.0) if effects else 70.0

    def use(self) -> bool:
        if self.limited_use:
            if self.uses > 0:
                self.uses -= 1
                return True
            return False
        return True

    def get_skill_modifier(self, skill_name: str) -> int:
        # Check standard "skill_modifiers" dict
        mods = self.effects.get("skill_modifiers", {})
        return mods.get(skill_name, 0)
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "effects": self.effects,
            "usable_in": self.usable_in,
            "limited_use": self.limited_use,
            "uses": self.uses
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class Evidence:
    def __init__(self, id: str, description: str, type: str, location: str = "unknown", collected_with: str = None, 
                 related_to: List[str] = None, timestamp: float = None, name: str = None,
                 related_skills: List[str] = None, analyzed: bool = False, related_npcs: List[str] = None):
        self.id = id
        self.name = name or id
        self.description = description
        self.type = type # physical, digital, testimony, etc.
        self.location = location
        self.collected_with = collected_with
        self.related_to = related_to or []
        self.timestamp = timestamp
        self.tags: List[str] = [] # e.g. "blood", "victim_1"
        
        # Week 6 additions
        self.related_skills = related_skills or []  # Skills that can analyze this
        self.analyzed = analyzed  # Whether forensic analysis has been performed
        self.analysis_results: Dict[str, str] = {}  # Skill -> result text
        self.related_npcs = related_npcs or []  # NPCs connected to this evidence

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)
    
    def analyze_with_skill(self, skill_name: str, result_text: str):
        """Mark evidence as analyzed with a specific skill and store results."""
        self.analyzed = True
        self.analysis_results[skill_name] = result_text
        print(f"[Evidence] {self.name} analyzed with {skill_name}")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "location": self.location,
            "collected_with": self.collected_with,
            "related_to": self.related_to,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "related_skills": self.related_skills,
            "analyzed": self.analyzed,
            "analysis_results": self.analysis_results,
            "related_npcs": self.related_npcs
        }
    
    @classmethod
    def from_dict(cls, data):
        obj = cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            description=data["description"],
            type=data["type"],
            location=data.get("location", "unknown"),
            collected_with=data.get("collected_with"),
            related_to=data.get("related_to", []),
            timestamp=data.get("timestamp"),
            related_skills=data.get("related_skills", []),
            analyzed=data.get("analyzed", False),
            related_npcs=data.get("related_npcs", [])
        )
        obj.tags = data.get("tags", [])
        obj.analysis_results = data.get("analysis_results", {})
        return obj


class EvidenceBoard:
    def __init__(self):
        self.nodes: Dict[str, Evidence] = {} # Keyed by evidence ID
        self.links: List[Dict[str, str]] = [] # {"from": id, "to": id, "reason": str}

    def add_evidence(self, evidence: Evidence):
        self.nodes[evidence.id] = evidence

    def link_evidence(self, id1: str, id2: str, reason: str = "Player Linked"):
        if id1 in self.nodes and id2 in self.nodes:
            self.links.append({"from": id1, "to": id2, "reason": reason})
            return True
        return False
    
    def to_dict(self):
        return {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "links": self.links
        }
    
    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.nodes = {k: Evidence.from_dict(v) for k, v in data.get("nodes", {}).items()}
        obj.links = data.get("links", [])
        return obj
    
    def get_display_string(self) -> str:
        s = "=== EVIDENCE BOARD ===\n"
        if not self.nodes:
            s += " (Empty)\n"
            return s
            
        for evid in self.nodes.values():
            s += f"[{evid.id}] ({evid.type}): {evid.description}\n"
            s += f"  Tags: {', '.join(evid.tags)}\n"
            
        s += "\n--- LINKS ---\n"
        if not self.links:
            s += " (No connections established)\n"
        for link in self.links:
            s += f" {link['from']} <--> {link['to']} ({link['reason']})\n"
            
        return s


class InventoryManager:
    def __init__(self):
        self.carried_items: List[Item] = []
        self.evidence_collection: Dict[str, Evidence] = {}
        self.board = EvidenceBoard()
        self.documents: List[Dict] = []
    
    def add_item(self, item: Item):
        self.carried_items.append(item)
        print(f"[Inventory] Added: {item.name}")

    def add_evidence(self, evidence: Evidence):
        self.evidence_collection[evidence.id] = evidence
        self.board.add_evidence(evidence)
        print(f"[Evidence] Collected: {evidence.id}")

    def get_modifiers_for_skill(self, skill_name: str) -> int:
        total = 0
        for item in self.carried_items:
            # Assuming we only get modifiers if we *have* the item. 
            # In complex systems we arguably need to 'equip' or 'use' it.
            # For this text adventure, possession implies potential usage or auto-assist.
            mod = item.get_skill_modifier(skill_name)
            if mod != 0:
                total += mod
        return total

    def list_inventory(self):
        print("\n=== INVENTORY ===")
        if not self.carried_items:
            print(" (Empty)")
        for item in self.carried_items:
            uses_str = f" ({item.uses} uses left)" if item.limited_use else ""
            print(f"- {item.name} [{item.type}]{uses_str}: {item.description}")
            if item.effects:
                 print(f"  Effects: {item.effects}")
                 
    def view_board(self):
        print(self.board.get_display_string())

    def to_dict(self):
        return {
            "carried_items": [i.to_dict() for i in self.carried_items],
            "evidence_collection": {k: v.to_dict() for k, v in self.evidence_collection.items()},
            "board": self.board.to_dict(),
            "documents": self.documents
        }
    
    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.carried_items = [Item.from_dict(i) for i in data.get("carried_items", [])]
        obj.evidence_collection = {k: Evidence.from_dict(v) for k, v in data.get("evidence_collection", {}).items()}
        obj.board = EvidenceBoard.from_dict(data.get("board", {}))
        obj.documents = data.get("documents", [])
        return obj
