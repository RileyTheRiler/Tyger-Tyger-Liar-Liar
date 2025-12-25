import random
from typing import List, Dict, Optional, Any

class AutopsyMinigame:
    """
    Manages a procedural examination of a body to find evidence.
    Errors in the sequence reduce 'body_integrity', making further findings harder or impossible.
    """
    def __init__(self, body_id: str, body_name: str, skill_system, inventory_manager):
        self.body_id = body_id
        self.body_name = body_name
        self.skill_system = skill_system
        self.inventory = inventory_manager
        
        self.integrity = 100.0
        self.zones_examined: Set[str] = set()
        self.completed = False
        
        self.ZONES = {
            "External": {"skill": "Forensics", "difficulty": 8, "desc": "Check for surface wounds and external markings."},
            "Internal organs": {"skill": "Medicine", "difficulty": 10, "desc": "Examine the chest cavity and internal organs."},
            "Brain": {"skill": "Medicine", "difficulty": 12, "desc": "Detailed analysis of brain structure and neural pathways."},
            "Toxicology": {"skill": "Forensics", "difficulty": 9, "desc": "Scan blood and fluids for foreign substances."}
        }
        
    def run_minigame(self, printer_func):
        """Standard interface for running the minigame in the terminal."""
        printer_func(f"\n=== AUTOPSY: {self.body_name} ===")
        printer_func(f"Integrity: {self.integrity}%")
        
        while not self.completed and self.integrity > 0:
            printer_func("\nSelect a zone to examine:")
            options = list(self.ZONES.keys())
            for i, zone in enumerate(options):
                status = "[DONE]" if zone in self.zones_examined else ""
                printer_func(f"{i+1}. {zone} {status}")
            
            printer_func(f"{len(options)+1}. Finish Examination")
            
            # Since this is for a text-game, we'd normally hook into the game loop
            # BUT for now we'll return the state to Game for input handling
            # or provide a local input loop if permitted.
            # In the current architecture, Game should call the 'examine_zone' method.
            break

    def examine_zone(self, zone_name: str) -> Dict[str, Any]:
        """Performs examination on a specific zone."""
        if zone_name not in self.ZONES:
            return {"success": False, "message": "Invalid zone."}
        
        if zone_name in self.zones_examined:
            return {"success": False, "message": "Zone already examined."}

        zone_data = self.ZONES[zone_name]
        skill = zone_data["skill"]
        difficulty = zone_data["difficulty"]
        
        # Integrity penalty: If integrity is low, difficulty increases
        effective_difficulty = difficulty + (100.0 - self.integrity) // 10
        
        result = self.skill_system.roll_check(skill, int(effective_difficulty))
        self.zones_examined.add(zone_name)
        
        if result["success"]:
            evidence_id = f"autopsy_{self.body_id}_{zone_name.lower().replace(' ', '_')}"
            findings = self._get_findings(zone_name)
            
            # Create evidence object logic would go here in Game.py
            return {
                "success": True,
                "message": f"Successfully examined {zone_name}.",
                "findings": findings,
                "evidence_id": evidence_id,
                "integrity_loss": 5.0 # Normal wear and tear
            }
        else:
            # Failure damages integrity significantly
            loss = 15.0
            self.integrity = max(0, self.integrity - loss)
            return {
                "success": False,
                "message": f"Failed to examine {zone_name}. You made a mistake during the procedure.",
                "integrity_loss": loss
            }

    def _get_findings(self, zone: str) -> str:
        findings_map = {
            "External": "Distinct geometrical patterns burned into the sub-dermal layer. Not human-made.",
            "Internal organs": "The heart has been replaced with a crystalline structure currently vibrating at a low frequency.",
            "Brain": "Neural pathways have been re-routed into a fractal pattern. The frontal lobe is completely hollowed out.",
            "Toxicology": "Blood contains traces of a bioluminescent fluid that identifies as neither organic nor inorganic."
        }
        return findings_map.get(zone, "Inconclusive results.")
    
    def conclude(self) -> str:
        self.completed = True
        if self.integrity <= 0:
            return "The body has been irreparably damaged. Further study is impossible."
        if len(self.zones_examined) == len(self.ZONES):
            return "Autopsy complete. You have extracted all possible data from the subject."
        return "Examination concluded prematurely."
