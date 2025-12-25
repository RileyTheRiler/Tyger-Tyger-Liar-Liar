"""
Corkboard Minigame - Evidence Linking System.
Allows players to manually connect clues to unlock hidden theories or trigger realizations.
"""

from typing import Dict, List, Optional, Tuple, Set
from board import Board
from inventory_system import InventoryManager, Evidence

# Eureka Patterns: Specific combinations of links that unlock theories
# Format: { (ev1_id, ev2_id): {"theory_id": "...", "message": "..."} }
# Sorting is used internally to make (A, B) same as (B, A)
EUREKA_LINKS = {
    frozenset(["aurora_footage", "blood_sample"]): {
        "theory_id": "the_entity_is_hostile",
        "message": "EUREKA! The blood pattern matches the aurora's frequency... it wasn't an accident. It was an attack."
    },
    frozenset(["population_log", "missing_report_01"]): {
        "theory_id": "kaltvik_is_a_prison",
        "message": "Wait... the numbers don't add up. Every arrival coincides with a disappearance. Exactly 347. Always."
    },
    frozenset(["old_map", "dew_line_report"]): {
        "theory_id": "the_missing_are_connected",
        "message": "The locations form a perfect geometric grid around the DEW Line station. They're being taken systematically."
    }
}

# False Trail Patterns: Misleading combinations that drain sanity
FALSE_TRAILS = {
    frozenset(["witness_statement_01", "unreliable_photo"]): {
        "sanity_drain": 10,
        "message": "You spent hours chasing a shadow. Your eyes hurt, and your mind feels frayed. It was just pareidolia."
    }
}

class CorkboardMinigame:
    def __init__(self, board: Board, inventory: InventoryManager):
        self.board = board
        self.inventory = inventory
        self.links = set() # Set of frozensets (pairs of evidence IDs)
        self.discovered_eurekas = set()

    def link_evidence(self, ev1_id: str, ev2_id: str) -> Dict:
        """
        Creates a link between two pieces of evidence.
        Checks for Eureka moments or False Trails.
        """
        if ev1_id == ev2_id:
            return {"success": False, "message": "You can't link a piece of evidence to itself."}

        # Check if evidence exists
        ev1 = self.inventory.evidence_collection.get(ev1_id)
        ev2 = self.inventory.evidence_collection.get(ev2_id)

        if not ev1 or not ev2:
            return {"success": False, "message": "One or both pieces of evidence not found."}

        link_pair = frozenset([ev1_id, ev2_id])
        
        if link_pair in self.links:
            return {"success": False, "message": "These clues are already linked on your board."}

        # Add the link
        self.links.add(link_pair)
        self.inventory.board.link_evidence(ev1_id, ev2_id, "Manual Link")
        
        result = {
            "success": True,
            "message": f"Linked: '{ev1.id}' ↔ '{ev2.id}'",
            "eureka": False,
            "false_trail": False
        }

        # Check for Eureka
        if link_pair in EUREKA_LINKS and link_pair not in self.discovered_eurekas:
            eureka_data = EUREKA_LINKS[link_pair]
            theory_id = eureka_data["theory_id"]
            
            # Unlock the theory
            if self.board.discover_theory(theory_id):
                self.discovered_eurekas.add(link_pair)
                result["eureka"] = True
                result["theory_id"] = theory_id
                result["message"] = eureka_data["message"]
            else:
                theory = self.board.get_theory(theory_id)
                if theory and theory.status != "locked":
                    # Already discovered or active
                    pass

        # Check for False Trail
        if link_pair in FALSE_TRAILS:
            trail_data = FALSE_TRAILS[link_pair]
            result["false_trail"] = True
            result["sanity_drain"] = trail_data["sanity_drain"]
            result["message"] = trail_data["message"]

        return result

    def get_corkboard_ui(self) -> str:
        """Renders the corkboard ASCII UI."""
        lines = []
        lines.append("╔═══════════════════════════════════════════════════════════╗")
        lines.append("║                   THE CORKBOARD                           ║")
        lines.append("╠═══════════════════════════════════════════════════════════╣")
        
        # List all evidence
        lines.append("║  [CLUES ON BOARD]                                         ║")
        for ev_id, ev in self.inventory.evidence_collection.items():
            desc = (ev.description[:40] + '...') if len(ev.description) > 40 else ev.description
            lines.append(f"║  • {ev_id.ljust(15)} : {desc.ljust(40)} ║")
        
        lines.append("║                                                           ║")
        lines.append("║  [CONNECTIONS]                                            ║")
        if not self.links:
            lines.append("║  (No strings attached yet...)                             ║")
        else:
            for link in self.links:
                ids = list(link)
                lines.append(f"║  • {ids[0]} ↔ {ids[1]}".ljust(61) + "║")
        
        lines.append("║                                                           ║")
        lines.append("╚═══════════════════════════════════════════════════════════╝")
        lines.append("Commands: 'link <ev1> <ev2>' | 'view <ev1>' | 'exit'")
        
        return "\n".join(lines)

    def run_minigame(self):
        """Interactive loop for the corkboard minigame."""
        print("\nYou step up to the corkboard. Red string and Polaroids cover the surface.")
        
        while True:
            print("\n" + self.get_corkboard_ui())
            cmd = input("\nCORKBOARD> ").strip().lower()
            
            if cmd == "exit":
                print("You step away from the corkboard.")
                break
            
            if cmd.startswith("link "):
                parts = cmd.split()
                if len(parts) >= 3:
                    ev1, ev2 = parts[1], parts[2]
                    result = self.link_evidence(ev1, ev2)
                    print(f"\n{result['message']}")
                    
                    if result.get("eureka"):
                        print(f"\n[NEW THEORY UNLOCKED: {result['theory_id']}]")
                    elif result.get("false_trail"):
                        print(f"\n[SANITY DRAIN: -{result['sanity_drain']}]")
                else:
                    print("Usage: link <evidence_id_1> <evidence_id_2>")
            
            elif cmd.startswith("view "):
                parts = cmd.split()
                if len(parts) >= 2:
                    ev_id = parts[1]
                    ev = self.inventory.evidence_collection.get(ev_id)
                    if ev:
                        print(f"\n[{ev.id}] ({ev.type})\n{ev.description}")
                    else:
                        print(f"Evidence '{ev_id}' not found.")
                else:
                    print("Usage: view <evidence_id>")
            else:
                print("Unknown command. Try 'link', 'view', or 'exit'.")
