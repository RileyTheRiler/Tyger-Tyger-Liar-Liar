from typing import Tuple, Optional
from tyger_game.engine.scene_manager import SceneManager
from tyger_game.engine.character import Character
from tyger_game.engine.dialogue import DialogueManager
from tyger_game.engine.skill_checks import perform_skill_check, format_check_result
from tyger_game.ui.interface import print_text, Colors

class CommandParser:
    def __init__(self, scene_manager: SceneManager, character: Character, dialogue_manager: DialogueManager):
        self.scene_manager = scene_manager
        self.character = character
        self.dialogue_manager = dialogue_manager

    def parse(self, input_text: str):
        """
        Parses raw input and executes actions.
        """
        if not input_text:
            return

        parts = input_text.lower().split()
        verb = parts[0]
        noun = " ".join(parts[1:]) if len(parts) > 1 else None

        if verb in ["quit", "exit"]:
            return "quit"

        elif verb in ["look", "l"]:
            if noun:
                self._handle_examine(noun)
            else:
                self._handle_look_scene()

        elif verb in ["examine", "x", "inspect"]:
            if noun:
                self._handle_examine(noun)
            else:
                print_text("Examine what?", Colors.WARNING)

        elif verb in ["go", "move", "walk"]:
            if noun:
                self._handle_move(noun)
            else:
                print_text("Go where?", Colors.WARNING)

        elif verb in ["talk", "speak", "chat"]:
            if noun:
                self._handle_talk(noun)
            else:
                print_text("Talk to whom?", Colors.WARNING)

        elif verb in ["check", "roll"]:
            # Debug command to test skills: "check logic 10"
            if noun:
                self._handle_debug_check(noun)
            else:
                print_text("Check usage: check <skill> [dc]", Colors.WARNING)

        elif verb in ["help", "h"]:
            print_text("Commands: look, examine <obj>, go <dir>, talk <npc>, check <skill>, quit", Colors.CYAN)
            
        else:
            # Simple directional shorthand
            exits = self.scene_manager.get_exits()
            if verb in exits:
                self._handle_move(verb)
            else:
                print_text("I don't understand that command.", Colors.FAIL)

    def _handle_look_scene(self):
        scene = self.scene_manager.current_scene
        if not scene:
            return
        
        print_text(f"== {scene.get('title', scene.get('id', 'Unknown'))} ==", Colors.HEADER)
        description = self.scene_manager.get_description(self.character)
        print_text(description)
        
        # Display Choices
        choices = self.scene_manager.get_choices()
        if choices:
            print_text("\nOPTIONS:", Colors.CYAN)
            for idx, choice in enumerate(choices):
                # Check conditions visibility? skipping for prototype simplicity
                label = choice.get("label", choice.get("text", "Unknown"))
                print_text(f"{idx + 1}. {label}")
        
        exits = scene.get('exits', {})
        if exits:
            exit_list = ", ".join(exits.keys())
            print_text(f"\nExits: {exit_list}", Colors.BLUE)

    def _handle_examine(self, noun: str):
        interactable_text = self.scene_manager.get_interactable(noun)
        if interactable_text:
            print_text(interactable_text)
        else:
            # Also check if it's an NPC
            # TODO: NPC descriptions should be in Interactables or Scene Data
            print_text(f"You see nothing special about the {noun}.")

    def _handle_move(self, direction: str):
        exits = self.scene_manager.get_exits()
        
        # Support numeric choice selection
        if direction in exits:
            next_scene_id = exits[direction]
            try:
                self.scene_manager.load_scene(next_scene_id)
                self._handle_look_scene()
            except FileNotFoundError:
                print_text(f"The path to '{next_scene_id}' is blocked (File missing).")
        else:
            print_text("You can't go that way.")

    def _handle_talk(self, noun: str):
        # 1. Check if NPC is in the scene (using interactables for now or a separate list)
        # For this prototype, we'll check if a dialogue file exists or if the literal noun is "receptionist"
        # Ideally, SceneManager should expose explicit NPCs.
        
        # HACK: Hardcoded for prototype or using interactables
        # If the noun is "receptionist" and we are in "lobby_interrogation"
        
        # Better: Check scene interactables for the key noun
        if not self.scene_manager.get_interactable(noun):
            print_text(f"There is no {noun} here.")
            return

        # 2. Try to load dialogue
        # Assuming npc_noun.json mapping
        dialogue_id = f"npc_{noun}"
        
        try:
            # Helper to load dialogue (TODO: Move to DialogueManager or SceneManager)
            import json, os
            path = os.path.join(self.scene_manager.data_path, "dialogues", f"{dialogue_id}.json")
            if not os.path.exists(path):
                 print_text(f"The {noun} has nothing to say.")
                 return
                 
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            root = data.get("root")
            if root:
                self.dialogue_manager.start_dialogue(root, self.character)
                # After dialogue, reprint scene?
                # self._handle_look_scene()
                
        except Exception as e:
            print_text(f"Error starting dialogue: {e}", Colors.FAIL)

    def _handle_debug_check(self, args: str):
        # Expected: "logic 10" or just "logic" (default DC 8)
        parts = args.split()
        skill_name_candidate = parts[0]
        
        # Fuzzy match skill name
        found_skill = None
        for attr, skills in self.character.skills.items():
             pass # Logic to match skills is complex without flat list access in Char
        
        # Check constants
        from tyger_game.utils.constants import SKILLS
        for s_list in SKILLS.values():
                for s in s_list:
                    if s.lower() == skill_name_candidate.lower():
                        found_skill = s
                        break
        
        if not found_skill:
            print_text(f"Skill '{skill_name_candidate}' not found.", Colors.FAIL)
            return

        dc = 8
        if len(parts) > 1:
            try:
                dc = int(parts[1])
            except ValueError:
                pass

        result = perform_skill_check(self.character, found_skill, dc)
        print_text(format_check_result(result), Colors.GREEN if result.success else Colors.FAIL)

