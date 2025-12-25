from typing import List, Dict, Callable
from tyger_game.ui.interface import print_text, get_input, Colors
from tyger_game.engine.character import Character
from tyger_game.engine.alignment_system import AlignmentSystem
from tyger_game.engine.skill_checks import perform_skill_check, format_check_result

class DialogueManager:
    def __init__(self):
        self.active = False
        self.character = None
    
    def start_dialogue(self, dialogue_node: Dict, character: Character):
        self.active = True
        self.character = character
        self._run_node(dialogue_node)

    def _run_node(self, node: Dict):
        while self.active:
            # 1. Passive Checks (Narrator interjections)
            if "passive_checks" in node:
                for check in node["passive_checks"]:
                    skill = check["skill"]
                    diff = check["difficulty"]
                    result = perform_skill_check(self.character, skill, diff, "passive")
                    if result.success:
                        print_text(format_check_result(result, skill), Colors.WARNING)
                        print_text(f"  Startled insight: {check['text']}", Colors.CYAN)

            # 2. Main Text
            print_text(f"{node.get('speaker', 'Unknown')}: \"{node.get('text', '...')}\"", Colors.CYAN)
            
            # 3. Filter Choices based on Prerequisites
            choices = []
            original_indices = []
            
            for i, choice in enumerate(node.get('choices', [])):
                # alignment checks
                req = choice.get("req_alignment")
                if req:
                    # e.g. "active_alignment" == "Fundamentalist"
                    # Simplified check for now
                    if self.character.active_alignment != req:
                        continue
                choices.append(choice)
                original_indices.append(i)

            if not choices:
                self.active = False
                return

            print("\n")
            for idx, choice in enumerate(choices):
                # Tagging (visual indicator of alignment)
                tag = ""
                if "tag" in choice: tag = f"[{choice['tag']}] "
                print(f"{idx + 1}. {tag}{choice['text']}")
            
            selection = get_input("\nChoose > ")
            
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(choices):
                    chosen = choices[idx]
                    
                    # 4. Apply Effects
                    if "effect" in chosen:
                        eff = chosen["effect"]
                        # Alignment shift
                        if "alignment" in eff:
                            axis = eff["alignment"]
                            val = eff.get("value", 1)
                            # Apply logic
                            new_arch = AlignmentSystem.modify_alignment(self.character, axis, val)
                            if new_arch:
                                print_text(f"*** EPISTEMIC SHIFT: {new_arch} ***", Colors.HEADER)
                    
                    if "internalize" in chosen:
                        from tyger_game.engine.paradigm_system import ParadigmManager
                        ParadigmManager.start_internalizing(self.character, chosen["internalize"])

                    # Logic to move to next node would go here (recursion or loop)
                    # For prototype, we just end or print
                    print_text(f"> You chose: {chosen['text']}")
                    
                    if "next_node" in chosen:
                        # In a real system, we'd load the next node by ID.
                        # recursing for now if next_node is a dict (demo structure)
                        if isinstance(chosen["next_node"], dict):
                            self._run_node(chosen["next_node"])
                            return
                        else:
                             # TODO: Fetch from scene data
                             self.active = False
                    else:
                        self.active = False
                else:
                    print_text("Invalid choice.", Colors.FAIL)
            except ValueError:
                print_text("Please enter a number.", Colors.FAIL)
