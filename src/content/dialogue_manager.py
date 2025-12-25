import json
import os
import random
from typing import Dict, List, Optional, Any, Tuple

class DialogueManager:
    def __init__(self, skill_system, board, player_state, npc_system=None):
        self.skill_system = skill_system
        self.board = board
        self.player_state = player_state
        self.npc_system = npc_system  # Week 12: For relationship gates
        
        self.current_dialogue_id = None
        self.current_npc_id = None  # Track which NPC we're talking to
        self.nodes = {}
        self.current_node_id = None
        self.active_interjections = []  # List of strings from passive checks
        
        # New Week 5 additions
        self.interrupt_data = {}
        self._load_interrupt_lines()
        
        # Debug flags
        self.debug_show_hidden = False

    def _load_interrupt_lines(self):
        """Loads passive interrupt lines from data/interrupt_lines.json."""
        path = os.path.join("data", "interrupt_lines.json")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.interrupt_data = json.load(f)
            except Exception as e:
                print(f"ERROR loading interrupt_lines.json: {e}")

    def load_dialogue(self, dialogue_id: str, dialogues_dir: str, npc_id: str = None):
        """Loads a dialogue tree from a JSON file."""
        path = os.path.join(dialogues_dir, f"{dialogue_id}.json")
        if not os.path.exists(path):
            print(f"ERROR: Dialogue file not found: {path}")
            return False
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.current_dialogue_id = dialogue_id
            self.current_npc_id = npc_id or data.get("npc_id")  # Track NPC
            
            # Support both old 'nodes' and new 'lines' format
            nodes_data = data.get("nodes", data.get("lines", []))
            self.nodes = {node["id"]: node for node in nodes_data}
            
            # Start at root, 'start' or first node
            if self.nodes:
                start_node = data.get("start_node", "start")
                if start_node not in self.nodes:
                    start_node = list(self.nodes.keys())[0]
                self.start_node(start_node)
                return True
            else:
                print("ERROR: No nodes in dialogue file.")
                return False
                
        except Exception as e:
            print(f"ERROR loading dialogue {dialogue_id}: {e}")
            return False

    def start_node(self, node_id: str):
        """Transitions to a new node and runs entry logic."""
        if node_id not in self.nodes:
            # Check if it's a special keyword or scene ID
            if node_id == "EXIT_DIALOGUE":
                self.current_node_id = None
            else:
                # Might be a scene transition handled by caller
                self.current_node_id = node_id
            return

        self.current_node_id = node_id
        node = self.nodes[node_id]
        
        # Run passive checks immediately
        self.active_interjections = self._run_passive_checks(node)
        
        # If this node is an automatic check, resolve it
        if "check" in node:
            self.resolve_automatic_check(node["check"])

    def _run_passive_checks(self, node: dict) -> List[str]:
        interjections = []
        
        # Get NPC context if available
        npc = None
        if self.npc_system and self.current_npc_id:
            npc = self.npc_system.get_npc(self.current_npc_id)
        
        # New Week 5 passives format: ["Empathy", "Perception"]
        passives = node.get("passives", [])
        # Old format: [{"skill": "...", "dc": ..., "interjection": "..."}]
        old_checks = node.get("passive_checks", [])
        
        # Handle new format
        for skill_name in passives:
            # Default DC 9 as per prompt
            res = self.skill_system.roll_check(skill_name, 9)
            if res["success"]:
                # Get flavor text from interrupt_data
                skill_interrupts = self.interrupt_data.get(skill_name, [])
                # interrupt_data is {skill: [list of strings]}, pick random one
                if skill_interrupts:
                    text = random.choice(skill_interrupts)
                else:
                    text = f"You notice something via {skill_name}."
                interjections.append(f"[{skill_name}] {text}")
            elif self.debug_show_hidden:
                interjections.append(f"[DEBUG FAIL {skill_name}]")
        
        # Handle old format (keeping for compatibility)
        for check in old_checks:
            skill_name = check.get("skill")
            dc = check.get("dc", 10)
            text = check.get("interjection", "")
            
            res = self.skill_system.roll_check(skill_name, dc)
            if res["success"]:
                interjections.append(text)
            elif self.debug_show_hidden:
                interjections.append(f"[DEBUG FAIL {skill_name} vs {dc}] {text}")
        
        # Week 11: NPC-driven passive checks
        if npc:
            # Empathy check for high fear
            if npc.fear > 70:
                res = self.skill_system.roll_check("Empathy", 9)
                if res["success"]:
                    interjections.append(f"[EMPATHY] {npc.name} is terrified. Their hands are shaking.")
            
            # Profiling check for disposition
            if npc.trust < 30:
                res = self.skill_system.roll_check("Profiling", 10)
                if res["success"]:
                    interjections.append(f"[PROFILING] {npc.name} doesn't trust you. Watch for deception.")
            
            # Authority check for relationship status
            status = npc.get_relationship_status()
            if status == "hostile":
                res = self.skill_system.roll_check("Authority", 11)
                if res["success"]:
                    interjections.append(f"[AUTHORITY] They're hostile. You'll need leverage to get cooperation.")
        
        # Week 11: Board theory commentary
        if self.board:
            active_theories = [t for t in self.board.theories.values() if t.status == "active"]
            for theory in active_theories:
                # Check if theory is relevant to this dialogue
                if self.current_dialogue_id and theory.id in self.current_dialogue_id:
                    interjections.append(f"[{theory.name.upper()}] This conversation relates to your theory...")
                
        return interjections

    def resolve_automatic_check(self, check_data: dict):
        """Resolves a skill check that triggers automatically on node entry."""
        skill_name = check_data["skill"]
        dc = check_data["dc"]
        
        check_type = "red" if check_data.get("red") else "white"
        check_id = check_data.get("white_id") or f"auto_{self.current_dialogue_id}_{self.current_node_id}"
        
        # Roll via skill system (handles red/white logic)
        result = self.skill_system.roll_check(skill_name, dc, check_type=check_type, check_id=check_id)
        
        # Store in player state for persistent tracking if needed
        if "failed_reds" not in self.player_state:
            self.player_state["failed_reds"] = []
        if "checked_whites" not in self.player_state:
            self.player_state["checked_whites"] = []
            
        if check_type == "red" and not result["success"]:
            if check_id not in self.player_state["failed_reds"]:
                self.player_state["failed_reds"].append(check_id)
        elif check_type == "white":
            if check_id not in self.player_state["checked_whites"]:
                self.player_state["checked_whites"].append(check_id)

        # Transition based on result
        if result["success"]:
            next_node = check_data.get("success_next")
        else:
            next_node = check_data.get("fail_next")
            
        if next_node:
            print(f"\n[CHECK: {skill_name} vs DC {dc}] -> {'SUCCESS' if result['success'] else 'FAILURE'}")
            self.start_node(next_node)

    def get_render_data(self):
        """Returns (speaker, text, interjections, choices) for the UI."""
        if not self.current_node_id or self.current_node_id not in self.nodes:
            return None
            
        node = self.nodes[self.current_node_id]
        
        # Filter/Process choices
        visible_choices = []
        for choice in node.get("choices", []):
            req_met, reason = self._check_requirements(choice)
            visible_choices.append({
                "text": choice.get("text", "..."),
                "enabled": req_met,
                "reason": reason, 
                "original_data": choice
            })
            
        return {
            "speaker": node.get("speaker", "???"),
            "text": node.get("text", "..."),
            "interjections": self.active_interjections,
            "choices": visible_choices
        }

    def _check_requirements(self, choice: dict) -> (bool, str):
        # 1. Skill Gates (Level check)
        if "skill_gate" in choice:
            gate = choice["skill_gate"]
            skill_name = gate.get("skill")
            level_req = gate.get("level", 0)
            
            skill = self.skill_system.get_skill(skill_name)
            if not skill or skill.effective_level < level_req:
                return False, f"[{skill_name} < {level_req}]"
                
        # 2. Theory conditions
        if "theory_req" in choice or "require_theory" in choice:
            t_id = choice.get("theory_req", choice.get("require_theory"))
            if not self.board.is_theory_active(t_id):
                return False, f"[Requires Theory: {t_id}]"
        
        # Week 12: Theory blocking
        if "theory_blocked" in choice:
            t_id = choice["theory_blocked"]
            if self.board.is_theory_active(t_id):
                return False, f"[Blocked by Theory: {t_id}]"
        
        # Week 12: Relationship gates
        if "relationship_gate" in choice and self.npc_system and self.current_npc_id:
            gate = choice["relationship_gate"]
            npc_id = gate.get("npc_id", self.current_npc_id)
            npc = self.npc_system.get_npc(npc_id)
            
            if npc:
                if "trust_min" in gate and npc.trust < gate["trust_min"]:
                    return False, f"[Trust < {gate['trust_min']}]"
                if "rapport_min" in gate and npc.rapport < gate["rapport_min"]:
                    return False, f"[Rapport < {gate['rapport_min']}]"
                if "respect_min" in gate and npc.respect < gate["respect_min"]:
                    return False, f"[Respect < {gate['respect_min']}]"
                if "fear_max" in gate and npc.fear > gate["fear_max"]:
                    return False, f"[Fear > {gate['fear_max']}]"
        
        # Week 12: Emotional flag requirements
        if "emotional_flag_required" in choice and self.npc_system and self.current_npc_id:
            required_flag = choice["emotional_flag_required"]
            npc = self.npc_system.get_npc(self.current_npc_id)
            if npc and required_flag not in npc.emotional_flags:
                return False, f"[Requires: {required_flag}]"
                
        return True, ""

    def select_choice(self, index: int):
        """Executes the choice at the given index from the last rendered list."""
        if not self.current_node_id or self.current_node_id not in self.nodes:
            return False, "Not in a dialogue node."
            
        node = self.nodes[self.current_node_id]
        choices = node.get("choices", [])
        
        if index < 0 or index >= len(choices):
            return False, "Invalid choice index."
            
        choice = choices[index]
        
        # Double check requirement
        allowed, _ = self._check_requirements(choice)
        if not allowed:
            return False, "Requirement not met."
            
        # Apply Effects
        if "effects" in choice:
            self._apply_effects(choice["effects"])
            
        # Move to next
        next_id = choice.get("next")
        
        if next_id == "EXIT_DIALOGUE":
            self.current_node_id = None
            return True, "EXIT"
        elif next_id and next_id in self.nodes:
            self.start_node(next_id)
            return True, "NEXT"
        else:
            return True, f"SCENE:{next_id}"

    def _apply_effects(self, effects: dict):
        if not effects: return
        
        if "sanity" in effects:
            self.player_state["sanity"] = max(0, min(100, self.player_state["sanity"] + effects["sanity"]))
            print(f" [Sanity {effects['sanity']:+}]")
            
        if "reality" in effects:
            self.player_state["reality"] = max(0, min(100, self.player_state["reality"] + effects["reality"]))
            print(f" [Reality {effects['reality']:+}]")
            
        if "theory_unlock" in effects:
            tid = effects["theory_unlock"]
            self.board.discover_theory(tid)
            print(f" [Theory Discovered: {tid}]")

    def process_input(self, raw_input: str) -> Tuple[bool, str]:
        """
        Process player input - supports both numbered choices and parser commands.
        Returns (success, message)
        """
        text = raw_input.strip()
        
        # Handle debug command
        if text == "/debug":
            self.toggle_debug()
            return True, "DEBUG_TOGGLE"
        
        # Try numeric choice first
        if text.isdigit():
            idx = int(text) - 1
            return self.select_choice(idx)
        
        # Parser commands: "ask about X", "say Y"
        lower = text.lower()
        
        # ASK ABOUT pattern
        if lower.startswith("ask about ") or lower.startswith("ask "):
            topic = lower.replace("ask about ", "").replace("ask ", "").strip()
            return self._handle_ask(topic)
        
        # SAY pattern
        if lower.startswith("say "):
            statement = text[4:].strip()  # Preserve case for statement
            return self._handle_say(statement)
        
        # Check for parser_triggers in current node
        node = self.nodes.get(self.current_node_id)
        if node and "parser_triggers" in node:
            triggers = node["parser_triggers"]
            for keyword, next_node in triggers.items():
                if keyword.lower() in lower:
                    self.start_node(next_node)
                    return True, "NEXT"
        
        return False, "I don't understand that."
    
    def _handle_ask(self, topic: str) -> Tuple[bool, str]:
        """Handle 'ask about X' commands."""
        # Check current node for topic-specific responses
        node = self.nodes.get(self.current_node_id)
        if node and "topics" in node:
            topics = node["topics"]
            for t in topics:
                if topic.lower() in t.get("keywords", []):
                    next_id = t.get("next")
                    if next_id:
                        self.start_node(next_id)
                        return True, "NEXT"
        
        # Check NPC knowledge if available
        if self.npc_system and self.current_npc_id:
            npc = self.npc_system.get_npc(self.current_npc_id)
            if npc:
                clue = npc.reveal_knowledge(topic)
                if clue:
                    return True, f"CLUE_REVEALED:{clue}"
        
        return False, f"They don't seem to know about '{topic}'."
    
    def _handle_say(self, statement: str) -> Tuple[bool, str]:
        """Handle 'say X' commands."""
        # For now, just check parser_triggers
        node = self.nodes.get(self.current_node_id)
        if node and "parser_triggers" in node:
            triggers = node["parser_triggers"]
            for keyword, next_node in triggers.items():
                if keyword.lower() in statement.lower():
                    self.start_node(next_node)
                    return True, "NEXT"
        
        return False, "They don't respond to that."

    def toggle_debug(self):
        self.debug_show_hidden = not self.debug_show_hidden
        print(f"[Dialogue Debug] Show Hidden: {self.debug_show_hidden}")
