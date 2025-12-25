from typing import List, Dict, Any, Optional

class BoardManager:
    def __init__(self, game_state):
        self.state = game_state

    def add_clue(self, clue_id: str, clue_data: dict):
        """Add a clue to the board and auto-link to theories."""
        # Add node if not exists
        node = {
            "id": clue_id,
            "type": "clue",
            "title": clue_data.get("title", clue_id),
            "summary": clue_data.get("text", ""),
            "tags": clue_data.get("tags", [])
        }
        self.state.add_board_node(node)
        
        # Auto-link
        links = clue_data.get("links_to_theories", [])
        for theory_id in links:
            # We add an edge. In a real system, we'd check if the theory is known.
            # Per requirements, we can auto-link even if theory isn't 'started'.
            self.state.add_board_edge(clue_id, theory_id, "supports")

    def start_theory(self, theory_id: str, theory_data: dict):
        """Add a theory to the board and start internalization."""
        node = {
            "id": theory_id,
            "type": "theory",
            "title": theory_data.get("title", theory_id),
            "summary": theory_data.get("summary", ""),
            "status": "internalizing",
            "time_remaining": theory_data.get("internalization_time", 60)
        }
        self.state.add_board_node(node)
    
    def update_internalization(self, minutes_passed: int):
        """Advance time on internalizing theories."""
        for node in self.state.board_graph["nodes"]:
            if node.get("type") == "theory" and node.get("status") == "internalizing":
                node["time_remaining"] -= minutes_passed
                if node["time_remaining"] <= 0:
                    node["time_remaining"] = 0
                    node["status"] = "internalized"
                    # Apply internalized effects? That would happen in game loop.

    def get_board_summary(self) -> str:
        """Textual summary of the board."""
        s = "=== INVESTIGATION BOARD ===\n"
        nodes = self.state.board_graph["nodes"]
        edges = self.state.board_graph["edges"]
        
        clues = [n for n in nodes if n["type"] == "clue"]
        theories = [n for n in nodes if n["type"] == "theory"]
        
        s += "\nCLUES:\n"
        for c in clues:
            s += f" - [{c['id']}] {c['title']}\n"
            
        s += "\nTHEORIES:\n"
        for t in theories:
            status = t.get('status', 'unknown')
            time = f" ({t.get('time_remaining')}m left)" if status == "internalizing" else ""
            s += f" - [{t['id']}] {t['title']} [{status.upper()}]{time}\n"
            
        s += "\nLINKS:\n"
        for e in edges:
            s += f" {e['from']} ---> {e['to']} ({e['type']})\n"
            
        return s
