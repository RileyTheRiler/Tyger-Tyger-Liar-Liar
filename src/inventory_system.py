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
    def __init__(self, id: str, description: str, type: str, location: str = "unknown", collected_with: str = None, related_to: List[str] = None, timestamp: float = None):
        self.id = id
        self.description = description
        self.type = type # physical, digital, testimony, etc.
        self.location = location
        self.collected_with = collected_with
        self.related_to = related_to or []
        self.timestamp = timestamp
        self.tags: List[str] = [] # e.g. "blood", "victim_1"

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "type": self.type,
            "location": self.location,
            "collected_with": self.collected_with,
            "related_to": self.related_to,
            "timestamp": self.timestamp,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data):
        obj = cls(
            id=data["id"],
            description=data["description"],
            type=data["type"],
            location=data.get("location", "unknown"),
            collected_with=data.get("collected_with"),
            related_to=data.get("related_to", []),
            timestamp=data.get("timestamp")
        )
        obj.tags = data.get("tags", [])
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
