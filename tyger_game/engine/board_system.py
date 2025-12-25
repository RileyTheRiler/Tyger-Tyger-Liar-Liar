from typing import List, Dict, Optional, Tuple
from tyger_game.engine.character import Character
from tyger_game.engine.alignment_system import AlignmentSystem
from tyger_game.ui.interface import print_text, Colors

class BoardNode:
    def __init__(self, nid: str, name: str, node_type: str, evidence_level: str = "SOFT"):
        self.id = nid
        self.name = name
        self.node_type = node_type # "FACT", "TESTIMONY", "THEORY", "ANOMALY"
        self.evidence_level = evidence_level # "HARD" (Physical), "SOFT" (Hearsay), "QUALIA" (Sensation)
        self.connections: List[str] = [] # List of connected Node IDs

class BoardSystem:
    def __init__(self):
        self.nodes: Dict[str, BoardNode] = {}
        self.active_hypothesis: Optional[str] = None

    def add_node(self, node: BoardNode):
        self.nodes[node.id] = node

    def connect_nodes(self, node_id_a: str, node_id_b: str, character: Character, force: bool = False) -> Dict:
        if node_id_a not in self.nodes or node_id_b not in self.nodes:
            print_text("Invalid nodes.", Colors.FAIL)
            return {"success": False, "error": "Invalid nodes."}

        node_a = self.nodes[node_id_a]
        node_b = self.nodes[node_id_b]

        # Epistemic Filter Check
        friction = self._calculate_friction(node_a, node_b, character)
        
        if friction > 0 and not force:
            print_text(f"[Friction Detected: {friction}%] 'This feels wrong... forced. Like I'm fitting a square peg in a round hole.'", Colors.WARNING)
            return {"success": False, "error": "Friction detected", "friction": friction}
            
        # If forced, apply penalty
        if friction > 0 and force:
            # Need to find psychological system to apply load
            # Assuming character has access or we need to pass it
            print_text(f"[Forcing Connection] A sharp headache blooms behind your eyes as you override your better judgment. [Mental Load +{friction // 2}]", Colors.FAIL)
            # Placeholder for actual mental load application - will check project structure for character/psych link
            if hasattr(character, 'modify_mental_load'):
                character.modify_mental_load(friction // 2, f"Epistemic Friction: {node_a.name} <-> {node_b.name}")
            elif "mental_load" in character.__dict__: # Fallback if direct access
                character.mental_load = min(100, character.mental_load + (friction // 2))

        # Store friction flag on nodes/links if needed for frontend
        node_a.connections.append({"id": node_id_b, "friction": friction > 0})
        node_b.connections.append({"id": node_id_a, "friction": friction > 0})
        
        print_text(f"Connected {node_a.name} <-> {node_b.name}", Colors.GREEN)
        
        return {"success": True, "friction": friction}

    def _calculate_friction(self, a: BoardNode, b: BoardNode, character: Character) -> int:
        """
        Returns a Friction Level (0-100) representing cognitive dissonance.
        """
        score_ratio = character.alignment_scores.get('skeptic', 0) - character.alignment_scores.get('believer', 0)
        has_paranormal = (a.node_type == "ANOMALY" or b.node_type == "ANOMALY")
        is_hard_evidence = (a.evidence_level == "HARD" and b.evidence_level == "HARD")

        # Case 1: The Skeptic's Block (Positive ratio = Skeptic)
        if score_ratio > 0 and has_paranormal and not is_hard_evidence:
            return min(100, score_ratio * 15) # Up to 100% friction

        # Case 2: The Believer's Dismissal (Negative ratio = Believer)
        if score_ratio < 0 and (a.node_type == "FACT" or b.node_type == "FACT") and is_hard_evidence:
            return min(100, abs(score_ratio) * 10)

        return 0

    def _validate_connection_alignment(self, a: BoardNode, b: BoardNode, character: Character) -> bool:
        # Legacy method - redirecting to friction
        return self._calculate_friction(a, b, character) == 0

    def get_redacted_node_data(self, node_id: str, character: Character) -> Dict:
        """
        Returns node data with descriptions redacted or modified based 
        on the character's epistemic alignment.
        """
        if node_id not in self.nodes:
            return {"error": "Node not found"}
            
        node = self.nodes[node_id]
        description = node.name # Using name as desc for now
        
        archetype = character.active_alignment or "Neutral"
        score_ratio = character.alignment_scores.get('skeptic', 0) - character.alignment_scores.get('believer', 0)
        
        final_desc = description
        is_glitched = False
        
        # 1. The Skeptic's Block: Redact Anomaly descriptions
        if (archetype == "Debunker" or score_ratio > 3) and node.node_type == "ANOMALY":
            if node.evidence_level != "HARD":
                final_desc = "█" * 10 + " [LOGICAL ERROR: CAUSALITY NOT ESTABLISHED] " + "█" * 5
                is_glitched = True
                
        # 2. The Believer's Dismissal: Redact mundane Facts
        elif (archetype == "Fundamentalist" or score_ratio < -3) and node.node_type == "FACT":
            if node.evidence_level == "HARD":
                final_desc = "[IRRELEVANT NOISE: THE MATERIAL PLANE IS A DECEPTION]"
                is_glitched = True
                
        return {
            "id": node.id,
            "name": node.name,
            "type": node.node_type,
            "evidence": node.evidence_level,
            "description": final_desc,
            "is_glitched": is_glitched
        }

    def check_for_resonance(self, character: Character) -> List[str]:
        """
        Scans the board for specific patterns of connected nodes.
        Returns a list of newly unlocked Paradigm IDs.
        """
        unlocked = []
        
        # Pattern 1: The Signal in the Static
        # Requires: 2+ Anomalies connected to each other, plus 1 Electronic Fact (hypothetical metadata)
        anomalies = [n for n in self.nodes.values() if n.node_type == "ANOMALY"]
        
        # Simple proximity check: Are there clusters of anomalies?
        anomaly_connections = 0
        for a in anomalies:
            for conn in a.connections:
                # conn is now a dict {"id": ..., "friction": ...}
                conn_id = conn["id"] if isinstance(conn, dict) else conn
                if conn_id in self.nodes and self.nodes[conn_id].node_type == "ANOMALY":
                    anomaly_connections += 1
        
        # If we have a cluster (each connection counted twice)
        if anomaly_connections >= 2:
            # Check if character already has it
            existing_ids = [p["id"] for p in character.paradigms]
            if "signal_in_static" not in existing_ids:
                unlocked.append("signal_in_static")
                
        return unlocked
