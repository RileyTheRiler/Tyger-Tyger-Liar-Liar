from typing import Dict, List, Optional, Tuple
from theories import THEORY_DATA

class Theory:
    def __init__(self, id_key: str, data: dict):
        self.id = id_key
        self.name = data["name"]
        self.category = data["category"]
        self.description = data["description"]
        self.hidden_effects = data.get("hidden_effects", False)
        self.effects = data.get("effects", {})
        self.conflicts_with = data.get("conflicts_with", [])
        self.internalize_time_hours = data.get("internalize_time_hours", 4)
        self.active_case = data.get("active_case", False)
        self.critical_for_endgame = data.get("critical_for_endgame", False)
        
        # Week 14: Requirements for discovery
        self.requirements = data.get("requirements", {
            "clues_required": [],
            "flags_required": [],
            "scenes_visited": [],
            "theories_active": [],
            "min_skill": {}
        })
        
        # Week 14: Unlocks when theory is active
        self.unlocks = data.get("unlocks", {
            "dialogue_options": [],
            "scene_inserts": [],
            "check_bonuses": {}
        })
        
        # Week 14: Effects applied when internalization completes
        self.on_internalize_effects = data.get("on_internalize_effects", [])
        
        # Week 14: Lens bias for narrative filtering
        self.lens_bias = data.get("lens_bias", "neutral")  # believer, skeptic, haunted, neutral
        
        # Degradation mechanics
        self.degradation_rate = data.get("degradation_rate", 10)  # % health lost per contradiction
        self.auto_locks = data.get("auto_locks", [])  # Theories locked when this is internalized
        self.health = 100.0  # Theory integrity (0-100)
        
        # State
        self.status = data.get("status", "available")  # active, internalizing, available, locked, closed
        self.internalization_progress_minutes = 0
        
        # Resolution tracking (for endgame)
        self.proven: Optional[bool] = None  # None = unresolved, True = proven, False = disproven
        self.evidence_count: int = 0  # Supporting evidence
        self.contradictions: int = 0  # Contradicting evidence
        self.linked_evidence: List[str] = []  # Evidence IDs

class Board:
    def __init__(self):
        self.max_slots = 3
        self.theories: Dict[str, Theory] = {}
        self._load_theories()
        
    def _load_theories(self):
        for key, data in THEORY_DATA.items():
            self.theories[key] = Theory(key, data)

    def get_theory(self, theory_id: str) -> Optional[Theory]:
        return self.theories.get(theory_id)

    def can_internalize(self, theory_id: str) -> Tuple[bool, str]:
        theory = self.get_theory(theory_id)
        if not theory:
            return False, "Theory not found."
            
        if theory.status != "available":
            return False, f"Theory is {theory.status}."
            
        if self.get_active_or_internalizing_count() >= self.max_slots:
            return False, "No available slots."
            
        # Check conflicts
        for other_id, other_t in self.theories.items():
            if other_t.status == "active" and (other_id in theory.conflicts_with or theory_id in other_t.conflicts_with):
                return False, f"Conflicts with active theory: {other_t.name}"

        return True, "OK"

    def start_internalizing(self, theory_id: str) -> bool:
        can, reason = self.can_internalize(theory_id)
        if not can:
            print(f"[BOARD] Cannot internalize {theory_id}: {reason}")
            return False

        theory = self.get_theory(theory_id)
        theory.status = "internalizing"
        theory.internalization_progress_minutes = 0
        
        # NEW: Apply auto-locks
        for locked_theory_id in theory.auto_locks:
            locked_theory = self.get_theory(locked_theory_id)
            if locked_theory and locked_theory.status == "available":
                locked_theory.status = "locked"
                print(f"[BOARD] Theory '{locked_theory.name}' is now incompatible and locked.")
        
        return True

    def on_time_passed(self, minutes: int) -> List[str]:
        messages = []
        for theory in self.theories.values():
            if theory.status == "internalizing":
                theory.internalization_progress_minutes += minutes
                required_minutes = theory.internalize_time_hours * 60
                
                if theory.internalization_progress_minutes >= required_minutes:
                    theory.status = "active"
                    messages.append(f"Theory Internalized: '{theory.name}'")
                    
        return messages

    def get_all_modifiers(self) -> Dict[str, int]:
        combined_effects = {}
        for theory in self.theories.values():
            if theory.status == "active":
                for skill, val in theory.effects.items():
                    combined_effects[skill] = combined_effects.get(skill, 0) + val
            # Optionally: internalizing theories might have partial or different effects? 
            # For now, only active ones apply.
        return combined_effects
        
    def get_active_or_internalizing_count(self) -> int:
        count = 0
        for t in self.theories.values():
            if t.status in ["active", "internalizing"]:
                count += 1
        return count

    def discover_theory(self, theory_id: str) -> bool:
        """Unlocks a theory, making it available for internalization."""
        theory = self.get_theory(theory_id)
        if not theory:
            return False
        if theory.status == "locked":
            theory.status = "available"
            return True
        return False

    def is_theory_active(self, theory_id: str) -> bool:
        """Check if a theory is currently active."""
        theory = self.get_theory(theory_id)
        return theory and theory.status == "active"

    def resolve_theory(self, theory_id: str, is_proven: bool) -> bool:
        """Mark a theory as proven or disproven."""
        theory = self.get_theory(theory_id)
        if not theory:
            return False
        
        theory.proven = is_proven
        print(f"[BOARD] Theory '{theory.name}' marked as {'PROVEN' if is_proven else 'DISPROVEN'}")
        return True

    def add_evidence_to_theory(self, theory_id: str, evidence_id: str) -> bool:
        """Link supporting evidence to a theory."""
        theory = self.get_theory(theory_id)
        if not theory:
            return False
        
        if evidence_id not in theory.linked_evidence:
            theory.linked_evidence.append(evidence_id)
            theory.evidence_count += 1
            print(f"[BOARD] Evidence linked to '{theory.name}' ({theory.evidence_count} total)")
            return True
        return False

    def add_contradiction_to_theory(self, theory_id: str, evidence_id: str) -> dict:
        """Link contradicting evidence to a theory and trigger degradation."""
        theory = self.get_theory(theory_id)
        if not theory:
            return {"success": False, "message": "Theory not found"}
        
        if evidence_id not in theory.linked_evidence:
            theory.linked_evidence.append(evidence_id)
            theory.contradictions += 1
            print(f"[BOARD] Contradiction found for '{theory.name}' ({theory.contradictions} total)")
            
            # NEW: Trigger degradation
            degradation_result = self.degrade_theory(theory_id, evidence_id)
            return {"success": True, **degradation_result}
        
        return {"success": False, "message": "Evidence already linked"}
    
    def degrade_theory(self, theory_id: str, evidence_id: str, base_sanity_penalty: int = 5) -> dict:
        """
        Contradicting evidence degrades theory health.
        If health reaches 0, theory closes and damages sanity.
        Returns dict with message and optional sanity_damage.
        """
        theory = self.get_theory(theory_id)
        if not theory or theory.status not in ["active", "internalizing"]:
            return {"message": "", "sanity_damage": 0}
        
        # Degrade theory health
        theory.health -= theory.degradation_rate
        theory.health = max(0, theory.health)
        
        if theory.health <= 0:
            # Theory has collapsed
            theory.status = "closed"
            theory.proven = False
            sanity_damage = base_sanity_penalty * theory.contradictions
            return {
                "message": f"⚠ Theory '{theory.name}' has COLLAPSED under contradictory evidence!",
                "sanity_damage": sanity_damage,
                "theory_collapsed": True
            }
        else:
            # Theory weakened but still standing
            return {
                "message": f"Theory '{theory.name}' weakened ({int(theory.health)}% integrity)",
                "sanity_damage": 0,
                "theory_collapsed": False
            }

    def get_resolution_summary(self) -> Dict[str, int]:
        """Get counts of proven/disproven/unresolved theories."""
        proven = 0
        disproven = 0
        unresolved = 0
        
        for theory in self.theories.values():
            if theory.status == "active":
                if theory.proven is True:
                    proven += 1
                elif theory.proven is False:
                    disproven += 1
                else:
                    unresolved += 1
        
        return {
            "proven": proven,
            "disproven": disproven,
            "unresolved": unresolved
        }

    def get_critical_theories(self) -> List[str]:
        """Get list of theories marked as critical for endgame."""
        critical = []
        for theory_id, theory in self.theories.items():
            if theory.critical_for_endgame:
                critical.append(theory_id)
        return critical
    
    def get_theory_health_status(self, theory_id: str) -> dict:
        """Get health status of a theory for UI display."""
        theory = self.get_theory(theory_id)
        if not theory:
            return {"exists": False}
        
        health_pct = int(theory.health)
        if health_pct >= 80:
            status = "Healthy"
        elif health_pct >= 50:
            status = "Weakened"
        elif health_pct >= 20:
            status = "Degraded"
        elif health_pct > 0:
            status = "Critical"
        else:
            status = "Collapsed"
        
        return {
            "exists": True,
            "health": health_pct,
            "status": status,
            "contradictions": theory.contradictions,
            "evidence_count": theory.evidence_count
        }

        return proven

        return {"nodes": nodes, "links": links}

    def get_board_data(self) -> dict:
        """
        Returns graph data for the frontend visualization.
        Nodes: Theories and Evidence
        Links: Relationships
        """
        nodes = []
        links = []
        
        # Helper for statuses
        status_colors = {
            "active": "#00ff00",       # Green
            "internalizing": "#ffff00", # Yellow
            "closed": "#ff0000",       # Red
            "proven": "#00ffff",       # Cyan
            "disproven": "#ff00ff",    # Magenta
            "gathered": "#cccccc"      # Grey (Evidence)
        }

        # Add Active/Internalizing Theories as Nodes
        for t_id, theory in self.theories.items():
            if theory.status not in ["active", "internalizing", "closed"]:
                continue
                
            # Determine color
            color = status_colors.get(theory.status, "#ffffff")
            if theory.proven is True: color = status_colors["proven"]
            elif theory.proven is False: color = status_colors["disproven"]
            elif theory.health < 20: color = "#ff4444" # Critical health red

            nodes.append({
                "id": t_id,
                "label": theory.name,
                "type": "theory",
                "status": theory.status,
                "health": theory.health,
                "proven": theory.proven,
                "color": color,
                "shape": "rect" # Visual hint
            })
            
            # Add Linked Evidence as Nodes and Links
            for ev_id in theory.linked_evidence:
                # Check if node exists (evidence might be linked to multiple theories)
                if not any(n["id"] == ev_id for n in nodes):
                    nodes.append({
                        "id": ev_id,
                        "label": ev_id, # Placeholder
                        "type": "evidence",
                        "status": "gathered",
                        "color": status_colors["gathered"],
                        "shape": "circle"
                    })
                
                links.append({
                    "source": ev_id,
                    "target": t_id,
                    "type": "supporting", 
                    "color": "#ff0000" if theory.status == "closed" else "#ffffff" # Red string styling
                })
    def to_dict(self) -> dict:
        """Serialize board state to dictionary."""
        theories_data = {}
        for t_id, theory in self.theories.items():
            theories_data[t_id] = {
                "status": theory.status,
                "internalization_progress_minutes": theory.internalization_progress_minutes,
                "health": theory.health,
                "proven": theory.proven,
                "evidence_count": theory.evidence_count,
                "contradictions": theory.contradictions,
                "linked_evidence": theory.linked_evidence
            }
        return {"theories": theories_data}

    @staticmethod
    def from_dict(data: dict) -> 'Board':
        """Deserialize board state from dictionary."""
        board = Board()
        if "theories" in data:
            for t_id, t_data in data["theories"].items():
                theory = board.get_theory(t_id)
                if theory:
                    theory.status = t_data.get("status", "available")
                    theory.internalization_progress_minutes = t_data.get("internalization_progress_minutes", 0)
                    theory.health = t_data.get("health", 100.0)
                    theory.proven = t_data.get("proven")
                    theory.evidence_count = t_data.get("evidence_count", 0)
                    theory.contradictions = t_data.get("contradictions", 0)
                    theory.linked_evidence = t_data.get("linked_evidence", [])
        return board

    # Week 14: New Methods
    
    def can_discover_theory(self, theory_id: str, game_state: dict) -> bool:
        """Check if theory requirements are met for discovery."""
        theory = self.get_theory(theory_id)
        if not theory or theory.status != "locked":
            return False
        
        reqs = theory.requirements
        
        # Check clues required
        if reqs.get("clues_required"):
            inventory = game_state.get("inventory_system")
            if inventory:
                for clue_id in reqs["clues_required"]:
                    if not inventory.has_item(clue_id):
                        return False
        
        # Check flags required
        if reqs.get("flags_required"):
            flags = game_state.get("player_flags", set())
            for flag in reqs["flags_required"]:
                if flag not in flags:
                    return False
        
        # Check scenes visited
        if reqs.get("scenes_visited"):
            visited = game_state.get("visited_scenes", set())
            for scene_id in reqs["scenes_visited"]:
                if scene_id not in visited:
                    return False
        
        # Check active theories required
        if reqs.get("theories_active"):
            for required_theory_id in reqs["theories_active"]:
                if not self.is_theory_active(required_theory_id):
                    return False
        
        # Check minimum skill levels
        if reqs.get("min_skill"):
            skill_system = game_state.get("skill_system")
            if skill_system:
                for skill_name, min_level in reqs["min_skill"].items():
                    if skill_system.get_skill_total(skill_name) < min_level:
                        return False
        
        return True
    
    def apply_internalize_effects(self, theory_id: str, game_instance) -> List[str]:
        """Apply on_internalize_effects when theory becomes active."""
        theory = self.get_theory(theory_id)
        if not theory:
            return []
        
        messages = []
        for effect in theory.on_internalize_effects:
            effect_type = effect.get("type")
            
            if effect_type == "set_flag":
                game_instance.player_state["event_flags"].add(effect["target"])
                messages.append(f"Flag set: {effect['target']}")
            
            elif effect_type == "modify_attention":
                if hasattr(game_instance, 'attention_system'):
                    game_instance.attention_system.modify_attention(effect["value"])
                    messages.append(f"Attention {'+' if effect['value'] > 0 else ''}{effect['value']}")
            
            elif effect_type == "modify_sanity":
                game_instance.player_state["sanity"] += effect["value"]
                messages.append(f"Sanity {'+' if effect['value'] > 0 else ''}{effect['value']}")
            
            elif effect_type == "modify_reality":
                game_instance.player_state["reality"] += effect["value"]
                messages.append(f"Reality {'+' if effect['value'] > 0 else ''}{effect['value']}")
            
            elif effect_type == "unlock_theory":
                unlocked_theory = self.get_theory(effect["target"])
                if unlocked_theory and unlocked_theory.status == "locked":
                    unlocked_theory.status = "available"
                    messages.append(f"Theory unlocked: {unlocked_theory.name}")
        
        return messages
    
    def get_active_theory_unlocks(self) -> dict:
        """Get all unlocks from currently active theories."""
        unlocks = {
            "dialogue_options": [],
            "scene_inserts": [],
            "check_bonuses": {}
        }
        
        for theory in self.theories.values():
            if theory.status == "active":
                # Dialogue options
                unlocks["dialogue_options"].extend(theory.unlocks.get("dialogue_options", []))
                
                # Scene inserts
                unlocks["scene_inserts"].extend(theory.unlocks.get("scene_inserts", []))
                
                # Check bonuses
                for skill, bonus in theory.unlocks.get("check_bonuses", {}).items():
                    unlocks["check_bonuses"][skill] = unlocks["check_bonuses"].get(skill, 0) + bonus
        
        return unlocks
