
class ObjectEditor:
    """
    Helper for generating object interaction JSON.
    """
    @staticmethod
    def create_object_template(name, description):
        return {
            name.lower().replace(" ", "_"): {
                "name": name,
                "description": description,
                "type": "interactable",
                "interactions": {
                    "use": {
                        "text": f"You use the {name}."
                    },
                    "examine": {
                        "text": description
                    }
                }
            }
        }

class InventoryBalancer:
    """
    Helper to check item weights and balance.
    """
    @staticmethod
    def check_balance(items_list):
        total_weight = sum(i.get("weight", 0) for i in items_list)
        print(f"Total Weight: {total_weight}")
        # Logic to suggest changes?
        pass

class EvidenceTracker:
    """
    Visualizes links between evidence, theories, and plot flags.
    """
    def __init__(self, board, player_state):
        self.board = board
        self.player_state = player_state

    def print_tracker(self):
        print("\n=== EVIDENCE TRACKER ===")

        # 1. Evidence Nodes
        print("\n--- Evidence Nodes ---")
        if not self.board.nodes:
            print(" (No evidence collected)")

        for evid_id, node in self.board.nodes.items():
            flags = [tag for tag in node.tags if tag in self.player_state.get("event_flags", set())]
            flag_str = f" (Active Flags: {', '.join(flags)})" if flags else ""
            print(f" [{evid_id}] {node.name}{flag_str}")

            # Check links
            links = [l for l in self.board.links if l["from"] == evid_id or l["to"] == evid_id]
            if links:
                for l in links:
                    other = l["to"] if l["from"] == evid_id else l["from"]
                    print(f"   -> Linked to {other} ({l['reason']})")

        # 2. Theory Connections (Implicit via Board class in game, but here we visualize)
        # Note: The 'Board' class in board.py manages theories separately from EvidenceBoard in inventory_system.
        # This is a slight architectural split. Ideally we'd query the main Board too.
        pass
