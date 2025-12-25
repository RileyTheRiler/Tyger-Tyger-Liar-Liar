"""
Memory System for Tyger Tyger Liar Liar
Manages suppressed memories that unlock based on conditions
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


@dataclass
class SuppressedMemory:
    """Represents a suppressed memory that can be unlocked."""
    id: str
    title: str
    scene_file: str  # Path to special scene JSON
    unlock_conditions: Dict[str, Any]
    revealed_truth: str  # What this memory reveals
    effects: Dict[str, int] = field(default_factory=dict)  # Stat changes on unlock
    unlocked: bool = False


class MemorySystem:
    """Manages suppressed memories and their unlock conditions."""
    
    def __init__(self, memories_file: str = "data/memories/memories.json"):
        self.memories: Dict[str, SuppressedMemory] = {}
        self.memories_file = memories_file
        self.load_memories()
    
    def load_memories(self) -> bool:
        """Load memory definitions from JSON file."""
        if not os.path.exists(self.memories_file):
            print(f"[MEMORY] Warning: Memory file not found: {self.memories_file}")
            return False
        
        try:
            with open(self.memories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for memory_id, memory_data in data.items():
                memory = SuppressedMemory(
                    id=memory_id,
                    title=memory_data["title"],
                    scene_file=memory_data["scene_file"],
                    unlock_conditions=memory_data["unlock_conditions"],
                    revealed_truth=memory_data["revealed_truth"],
                    effects=memory_data.get("effects", {}),
                    unlocked=False
                )
                self.memories[memory_id] = memory
            
            print(f"[MEMORY] Loaded {len(self.memories)} suppressed memories")
            return True
            
        except Exception as e:
            print(f"[MEMORY] Error loading memories: {e}")
            return False
    
    def check_unlock_conditions(self, memory: SuppressedMemory, game_state: Dict[str, Any]) -> bool:
        """
        Check if a memory's unlock conditions are met.
        
        Args:
            memory: The memory to check
            game_state: Dictionary containing:
                - skill_system: SkillSystem instance
                - player_state: Player state dict
                - board: Board instance
                - current_scene: Current scene ID
                - event_flags: Set of event flags
        
        Returns:
            True if all conditions are met
        """
        conditions = memory.unlock_conditions
        
        # Check skill threshold
        if "skill_threshold" in conditions:
            skill_system = game_state.get("skill_system")
            if not skill_system:
                return False
            
            for skill_name, required_level in conditions["skill_threshold"].items():
                skill = skill_system.get_skill(skill_name)
                if not skill or skill.effective_level < required_level:
                    return False
        
        # Check scene visited
        if "scene_visited" in conditions:
            current_scene = game_state.get("current_scene")
            required_scene = conditions["scene_visited"]
            if current_scene != required_scene:
                return False
        
        # Check theory active
        if "theory_active" in conditions:
            board = game_state.get("board")
            if not board:
                return False
            
            theory_id = conditions["theory_active"]
            if not board.is_theory_active(theory_id):
                return False
        
        # Check stat threshold (below threshold triggers)
        if "stat_threshold" in conditions:
            player_state = game_state.get("player_state")
            if not player_state:
                return False
            
            for stat_name, threshold in conditions["stat_threshold"].items():
                current_value = player_state.get(stat_name, 100)
                if current_value >= threshold:  # Must be BELOW threshold
                    return False
        
        # Check event flag
        if "event_flag" in conditions:
            event_flags = game_state.get("event_flags", set())
            required_flag = conditions["event_flag"]
            if required_flag not in event_flags:
                return False
        
        return True
    
    def check_memory_triggers(self, game_state: Dict[str, Any]) -> List[str]:
        """
        Check all locked memories for unlock conditions.
        
        Returns:
            List of memory IDs that were just unlocked
        """
        newly_unlocked = []
        
        for memory_id, memory in self.memories.items():
            if not memory.unlocked:
                if self.check_unlock_conditions(memory, game_state):
                    self.unlock_memory(memory_id)
                    newly_unlocked.append(memory_id)
        
        return newly_unlocked
    
    def unlock_memory(self, memory_id: str) -> bool:
        """
        Mark a memory as unlocked.
        
        Returns:
            True if memory was successfully unlocked
        """
        memory = self.memories.get(memory_id)
        if not memory:
            return False
        
        if memory.unlocked:
            return False  # Already unlocked
        
        memory.unlocked = True
        print(f"\n{'='*60}")
        print(f"  SUPPRESSED MEMORY SURFACING")
        print(f"{'='*60}")
        print(f"  {memory.title}")
        print(f"  \"{memory.revealed_truth}\"")
        print(f"{'='*60}\n")
        
        return True
    
    def get_memory(self, memory_id: str) -> Optional[SuppressedMemory]:
        """Get a specific memory by ID."""
        return self.memories.get(memory_id)
    
    def get_unlocked_memories(self) -> List[SuppressedMemory]:
        """Get all unlocked memories."""
        return [m for m in self.memories.values() if m.unlocked]
    
    def get_locked_memories(self) -> List[SuppressedMemory]:
        """Get all still-locked memories."""
        return [m for m in self.memories.values() if not m.unlocked]
    
    def get_memory_scene_path(self, memory_id: str) -> Optional[str]:
        """Get the full path to a memory's scene file."""
        memory = self.memories.get(memory_id)
        if not memory:
            return None
        
        # Construct full path
        base_dir = os.path.dirname(self.memories_file)
        return os.path.join(base_dir, memory.scene_file)
    
    def export_state(self) -> Dict[str, Any]:
        """Export memory system state for saving."""
        return {
            "unlocked_memories": [m.id for m in self.memories.values() if m.unlocked]
        }
    
    def load_state(self, data: Dict[str, Any]):
        """Load memory system state from save data."""
        unlocked_ids = data.get("unlocked_memories", [])
        for memory_id in unlocked_ids:
            if memory_id in self.memories:
                self.memories[memory_id].unlocked = True
