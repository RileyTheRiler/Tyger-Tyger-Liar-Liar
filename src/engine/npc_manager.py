from typing import Dict, Any, Optional
import json
import os

class NPCManager:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.npcs: Dict[str, Dict[str, Any]] = {}
        self._load_npcs()

    def _load_npcs(self):
        """Loads NPC initial states from data files (placeholder logic for now)."""
        # In a full implementation, this would load from data/npcs/*.json
        # For now, we initialize core NPCs with default values
        self.npcs = {
            "maude": {
                "name": "Maude",
                "phase": "wall", # wall, crack, collapse
                "trust": 10,
                "fear": 0,
                "location": "hotel_lobby"
            },
            "old_tom": {
                "name": "Old Tom",
                "phase": "omen", # omen, absence, echo
                "trust": 50,
                "fear": 0,
                "location": "maintenance_shed"
            },
            "dr_correl": {
                "name": "Dr. Correl",
                "phase": "anchor", # anchor, anomaly, conversion
                "trust": 40,
                "fear": 0,
                "location": "clinic"
            }
        }

    def get_npc(self, npc_id: str) -> Optional[Dict[str, Any]]:
        return self.npcs.get(npc_id)

    def get_npc_phase(self, npc_id: str) -> str:
        npc = self.get_npc(npc_id)
        if npc:
            return npc.get("phase", "unknown")
        return "unknown"

    def set_npc_phase(self, npc_id: str, new_phase: str):
        if npc_id in self.npcs:
            self.npcs[npc_id]["phase"] = new_phase

    def modify_trust(self, npc_id: str, amount: int):
        if npc_id in self.npcs:
            self.npcs[npc_id]["trust"] = max(0, min(100, self.npcs[npc_id]["trust"] + amount))

    def modify_fear(self, npc_id: str, amount: int):
         if npc_id in self.npcs:
             self.npcs[npc_id]["fear"] = max(0, min(100, self.npcs[npc_id]["fear"] + amount))

    def get_ui_data(self) -> Dict[str, Any]:
        """Returns a simplified dict for the frontend/board."""
        return {
            id: {
                "name": data["name"],
                "trust": data["trust"],
                "fear": data["fear"],
                "phase": data["phase"]
            }
            for id, data in self.npcs.items()
        }
