from typing import List, Dict, Optional, Set, Any
import re

class LiarEngine:
    """
    Detects contradictions between composed narrative text and gathered evidence.
    Triggers passive Skepticism checks when a discrepancy is found.
    """
    
    def __init__(self, skill_system, inventory_manager):
        self.skill_system = skill_system
        self.inventory = inventory_manager
        
    def check_contradictions(self, text: str) -> List[Dict]:
        """
        Scans text for keywords that conflict with evidence tags.
        Returns a list of structured Skepticism interjections.
        """
        interrupts = []
        
        # Mapping of keywords in text to evidence tags that contradict them
        # Format: "regex": {"tag": "evidence_tag", "message": "..."}
        contradiction_map = {
            r"no one (?:.+)?(was there|around)": {
                "tag": "witness_seen",
                "message": "They're lying. You have a witness who says otherwise."
            },
            r"no (?:records|file)": {
                "tag": "police_record",
                "message": "The precinct files you saw prove this is a lie."
            },
            r"(?:never|not) (?:actually )?(stopped|ceased)": {
                "tag": "ongoing_activity",
                "message": "Wait... your findings suggest it never actually stopped."
            },
            r"(?:at home|all night)": {
                "tag": "camera_footage_woods",
                "message": "The VHS tape shows them at the treeline at 03:00. Liar."
            },
            r"never seen (?:the |any )?(lights|aurora)": {
                "tag": "aurora_footage",
                "message": "Liars... everyone in this town has seen it. You have the tape."
            }
        }
        
        evidence_tags = self._get_player_evidence_tags()
        
        for pattern, data in contradiction_map.items():
            if re.search(pattern, text, re.IGNORECASE):
                if data["tag"] in evidence_tags:
                    # Trigger Skepticism check
                    check = self.skill_system.roll_check("Skepticism", 8, "hidden")
                    if check["success"]:
                        interrupts.append({
                            "skill": "SKEPTICISM",
                            "color": "purple",
                            "text": data["message"],
                            "icon": "skepticism"
                        })
                        
        return interrupts
        
    def _get_player_evidence_tags(self) -> Set[str]:
        tags = set()
        for ev in self.inventory.evidence_collection.values():
            tags.update(ev.tags)
            # Also include ID as a tag for simple matching
            tags.add(ev.id)
        return tags
