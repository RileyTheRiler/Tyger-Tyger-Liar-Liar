from typing import Dict, Any, List, Optional
from inventory_system import InventoryManager, Item
from mechanics import SkillSystem
import random

class InteractionManager:
    """
    Handles complex interactions between the player (tools, skills) and world objects.
    """
    def __init__(self, skill_system: SkillSystem, inventory_system: InventoryManager, player_state: Dict):
        self.skill_system = skill_system
        self.inventory_system = inventory_system
        self.player_state = player_state

    def interact(self, verb: str, tool_name: Optional[str], target_obj: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Main entry point for interactions.
        :param verb: The action verb (USE, SWAB, RECORD, etc.)
        :param tool_name: The name/ID of the tool being used (or None)
        :param target_obj: The data dict of the target object from scene
        :param context: Context data like current scene, etc.
        :return: Result string to display
        """
        interactions = target_obj.get("interactions", {})

        # 1. Normalize Tool
        # If verb is USE and tool_name is provided, we look for interaction key "use <tool_name>" or just "use"
        # If verb is specific (e.g. SWAB), we treat it as the action key.

        action_key = verb.lower()
        if tool_name:
            action_key = f"{verb.lower()} {tool_name.lower()}"

            # Check if player actually has the tool
            # (Unless tool is implicit/body part)
            if not self._player_has_tool(tool_name):
                 return f"You don't have a '{tool_name}'."

        # 2. Find Interaction Definition
        # We search for keys in `interactions` that match `action_key` or fallback.
        # e.g. "use uv light", "swab", "record evp"

        definition = self._find_interaction_definition(interactions, action_key, tool_name)

        if not definition:
            if tool_name:
                return f"You can't {verb.lower()} the {target_obj.get('name', 'target')} with {tool_name}."
            return f"You can't {verb.lower()} that."

        # 3. Process Requirements
        if not self._check_requirements(definition):
             return definition.get("failure_text", "You can't do that right now.")

        # 4. Process Skill Check
        if "skill_check" in definition:
            check = definition["skill_check"]
            skill_name = check["skill"]
            dc = check["difficulty"]

            result = self.skill_system.roll_check(skill_name, dc)
            if not result["success"]:
                # FAILURE
                fail_outcome = check.get("on_fail", {})
                return self._apply_outcome(fail_outcome, target_obj)
            else:
                # SUCCESS
                # Optional success override/addition
                success_outcome = check.get("on_success", {})
                if success_outcome:
                     self._apply_outcome(success_outcome, target_obj)
                # Continue to base outcome

        # 5. Direct Outcome (No skill check)
        return self._apply_outcome(definition, target_obj)

    def _player_has_tool(self, tool_name: str) -> bool:
        # Check inventory
        if self.inventory_system.get_item_by_name(tool_name):
            return True
        # Allow implicit tools if needed (e.g. "hands")
        if tool_name.lower() in ["hands", "self"]:
            return True
        return False

    def _find_interaction_definition(self, interactions: Dict, action_key: str, tool_name: Optional[str]) -> Optional[Dict]:
        # 1. Exact match (e.g. "use uv light", "swab forensics kit")
        if action_key in interactions:
            return interactions[action_key]

        # 2. Fallback: Verb only (e.g. "swab" when key was "swab forensics kit")
        # If action_key is "swab forensics kit", we might want to check "swab"
        verb_only = action_key.split(" ")[0]
        if verb_only in interactions:
            return interactions[verb_only]

        # 3. Fallback: Tool only (e.g. "uv light" when action was "use uv light")
        if tool_name and tool_name.lower() in interactions:
             return interactions[tool_name.lower()]

        return None

    def _check_requirements(self, definition: Dict) -> bool:
        reqs = definition.get("requirements", {})

        if "state" in reqs:
            # Check object state? (Not passed in currently, need state manager)
            pass

        return True

    def _apply_outcome(self, outcome: Dict, target_obj: Dict) -> str:
        text = outcome.get("text", "Done.")

        # Loot / Item Yield
        if "yield_item" in outcome:
            item_data = outcome["yield_item"]
            item = Item.from_dict(item_data)
            if self.inventory_system.add_item(item):
                text += f"\n[Received: {item.name}]"
            else:
                text += f"\n[Could not carry: {item.name}]"

        # Evidence Yield
        if "yield_evidence" in outcome:
            ev_data = outcome["yield_evidence"]
            # Contamination Check
            if outcome.get("contamination_risk", False):
                # If this was a failure branch, maybe mark contaminated?
                # Or based on tool used?
                pass

            # Create evidence object
            from inventory_system import Evidence
            ev = Evidence.from_dict(ev_data)

            # Apply tags
            if "add_tags" in outcome:
                for tag in outcome["add_tags"]:
                    ev.add_tag(tag)

            self.inventory_system.add_evidence(ev)
            text += f"\n[Evidence Collected: {ev.name}]"

        # State Change (Modify target object in place - temporary until reload)
        if "new_state" in outcome:
            target_obj.update(outcome["new_state"])

        # Player Flags
        if "set_flag" in outcome:
            flag = outcome["set_flag"]
            if "event_flags" in self.player_state:
                self.player_state["event_flags"].add(flag)

        # Sanity/Reality effects
        if "sanity" in outcome:
            val = outcome["sanity"]
            self.player_state["sanity"] += val
            text += f" [Sanity {'+' if val>0 else ''}{val}]"

        return text
