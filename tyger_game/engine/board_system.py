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

    def connect_nodes(self, node_id_a: str, node_id_b: str, character: Character) -> bool:
        if node_id_a not in self.nodes or node_id_b not in self.nodes:
            print_text("Invalid nodes.", Colors.FAIL)
            return False

        node_a = self.nodes[node_id_a]
        node_b = self.nodes[node_id_b]

        # Epistemic Filter Check
        if not self._validate_connection_alignment(node_a, node_b, character):
            return False
            
        # Success
        node_a.connections.append(node_id_b)
        node_b.connections.append(node_id_a)
        print_text(f"Connected {node_a.name} <-> {node_b.name}", Colors.GREEN)
        
        # Check for synthesis/conclusion...
        return True

    def _validate_connection_alignment(self, a: BoardNode, b: BoardNode, character: Character) -> bool:
        """
        Determines if the character's worldview allows this connection.
        """
        archetype = character.active_alignment or "Neutral"
        score_ratio = character.alignment_scores.get('skeptic', 0) - character.alignment_scores.get('believer', 0)

        # Logic: Connecting "Paranormal" to "Physical" 
        has_paranormal = (a.node_type == "ANOMALY" or b.node_type == "ANOMALY")
        
        # Filter 1: The Skeptic's Block
        # If highly skeptical, cannot connect Anomaly to Fact without Hard Evidence
        if score_ratio > 2 and has_paranormal:
            is_hard_evidence = (a.evidence_level == "HARD" and b.evidence_level == "HARD")
            if not is_hard_evidence:
                print_text("[Logic] 'There is no causal link here. You are grasping at straws.'", Colors.WARNING)
                return False

        # Filter 2: The Believer's Apophenia
        # (This would technically AUTO-connect things, but for manual play we might just allow loose connections)
        
        return True
