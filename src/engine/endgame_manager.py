"""
Endgame Manager for Tyger Tyger Liar Liar
Handles endgame triggers, ending determination, and final sequences
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple


class EndgameManager:
    """Manages endgame triggers, identity collapse, and ending paths."""
    
    # Thresholds
    CRITICAL_SANITY = 0
    CRITICAL_REALITY = 0
    IDENTITY_COLLAPSE_THRESHOLD = 20
    
    # Ending Categories
    ENDING_RATIONALITY = "rationality"
    ENDING_CONSPIRACY = "conspiracy"
    ENDING_COLLAPSE = "collapse"
    ENDING_CORRUPTION = "corruption"
    ENDING_REDEMPTION = "redemption"
    
    def __init__(self, board, player_state: Dict[str, Any], skill_system):
        self.board = board
        self.player_state = player_state
        self.skill_system = skill_system
        
        self.triggered = False
        self.trigger_reason = ""
        self.ending_path: Optional[str] = None
    
    def check_endgame_triggers(self) -> Tuple[bool, str]:
        """
        Check if any endgame condition is met.
        
        Returns:
            (triggered: bool, reason: str)
        """
        if self.triggered:
            return True, self.trigger_reason
        
        sanity = self.player_state.get("sanity", 50)
        reality = self.player_state.get("reality", 50)
        
        # 1. Critical mental state
        if sanity <= self.CRITICAL_SANITY:
            self.triggered = True
            self.trigger_reason = "Sanity collapsed to zero"
            return True, self.trigger_reason
        
        if reality <= self.CRITICAL_REALITY:
            self.triggered = True
            self.trigger_reason = "Reality perception completely fractured"
            return True, self.trigger_reason
        
        # 2. Critical theory proven/disproven
        critical_theories = self.board.get_critical_theories()
        for theory_id in critical_theories:
            theory = self.board.get_theory(theory_id)
            if theory and theory.proven is not None:
                self.triggered = True
                status = "proven" if theory.proven else "disproven"
                self.trigger_reason = f"Critical theory '{theory.name}' {status}"
                return True, self.trigger_reason
        
        # 3. All active case theories closed
        resolution = self.board.get_resolution_summary()
        active_cases = [t for t in self.board.theories.values() 
                       if t.active_case and t.status == "active"]
        
        if active_cases:
            all_resolved = all(t.proven is not None for t in active_cases)
            if all_resolved and len(active_cases) > 0:
                self.triggered = True
                self.trigger_reason = "All active cases resolved"
                return True, self.trigger_reason
        
        # 4. Special event flags
        event_flags = self.player_state.get("event_flags", set())
        if "submit_report" in event_flags:
            self.triggered = True
            self.trigger_reason = "Investigation report submitted"
            return True, self.trigger_reason
        
        if "leave_town" in event_flags:
            self.triggered = True
            self.trigger_reason = "Left Tyger Tyger"
            return True, self.trigger_reason
        
        return False, ""
    
    def check_identity_collapse_threshold(self) -> bool:
        """Returns True if identity collapse mechanics should be active."""
        reality = self.player_state.get("reality", 50)
        return reality < self.IDENTITY_COLLAPSE_THRESHOLD
    
    def apply_identity_distortion(self, text: str) -> str:
        """
        Apply reality-based distortion to narrative text.
        
        Reality levels:
        - 75-100: Normal
        - 50-74: Minor sensory additions
        - 25-49: Skill voice conflicts
        - 0-24: Fragmented reality
        """
        reality = self.player_state.get("reality", 100)
        
        if reality >= 75:
            return text
        
        # Level 1: Minor sensory additions (50-74)
        if reality >= 50:
            additions = [
                " (Did you hear that?)",
                " (The shadows seem darker.)",
                " (Something feels wrong.)",
                " (You're being watched.)"
            ]
            if random.random() < 0.3:
                text += random.choice(additions)
        
        # Level 2: Word replacements (25-49)
        elif reality >= 25:
            replacements = {
                "door": "mouth",
                "window": "eye",
                "light": "burning gaze",
                "shadow": "living void",
                "wall": "skin",
                "floor": "flesh",
                "ceiling": "skull",
                "room": "cage"
            }
            
            words = text.split()
            new_words = []
            for word in words:
                lower_word = word.lower().strip('.,!?;:')
                if lower_word in replacements and random.random() < 0.4:
                    # Preserve punctuation
                    punct = ''.join(c for c in word if c in '.,!?;:')
                    new_words.append(replacements[lower_word] + punct)
                else:
                    new_words.append(word)
            text = " ".join(new_words)
            
            # Add skill voice conflicts
            if random.random() < 0.5:
                conflicts = [
                    "\n\n[LOGIC]: This isn't real.\n[SUBCONSCIOUS]: It's always been real.",
                    "\n\n[SKEPTICISM]: Hallucination.\n[PARANORMAL SENSITIVITY]: Truth.",
                    "\n\n[COMPOSURE]: Stay calm.\n[INSTINCT]: RUN."
                ]
                text += random.choice(conflicts)
        
        # Level 3: Fragmented reality (0-24)
        else:
            # Severe distortions
            if random.random() < 0.6:
                fragments = [
                    "\n\nTHEY ARE WATCHING YOU.",
                    "\n\nYou've been here before. You'll be here again.",
                    "\n\nThe Tyger burns. The Tyger always burns.",
                    "\n\nWHICH ONE ARE YOU?",
                    "\n\n[ERROR: MEMORY CORRUPTED]"
                ]
                text += random.choice(fragments)
            
            # Recursive loops
            if random.random() < 0.3:
                text = text + "\n\n" + text[:50] + "..."
        
        return text
    
    def calculate_ending_path(self) -> str:
        """
        Determine which ending path the player has earned.
        
        Returns:
            Ending category string
        """
        sanity = self.player_state.get("sanity", 50)
        reality = self.player_state.get("reality", 50)
        resolution = self.board.get_resolution_summary()
        
        # Get skill levels
        empathy_skill = self.skill_system.get_skill("Empathy")
        empathy_level = empathy_skill.effective_level if empathy_skill else 0
        
        fortitude_skill = self.skill_system.get_skill("Fortitude")
        fortitude_level = fortitude_skill.effective_level if fortitude_skill else 0
        
        skepticism_skill = self.skill_system.get_skill("Skepticism")
        skepticism_level = skepticism_skill.effective_level if skepticism_skill else 0
        
        moral_corruption = self.player_state.get("moral_corruption_score", 0)
        
        # C. Psychological Collapse (highest priority)
        if sanity <= 10 or reality <= 10:
            return self.ENDING_COLLAPSE
        
        # A. Resolution through Rationality
        # High reality, all supernatural theories disproven, high skepticism
        if (reality > 60 and 
            resolution["disproven"] > 0 and 
            resolution["proven"] == 0 and
            skepticism_level >= 3):
            return self.ENDING_RATIONALITY
        
        # If theories were proven, distinguish between B, D, E
        if resolution["proven"] > 0:
            # D. Moral Corruption
            if moral_corruption >= 5 or empathy_level < 3:
                return self.ENDING_CORRUPTION
            
            # E. Self-Recovery / Redemption
            if empathy_level >= 4 or fortitude_level >= 4:
                return self.ENDING_REDEMPTION
            
            # B. Conspiracy Confirmed (neutral path)
            return self.ENDING_CONSPIRACY
        
        # Default fallback
        return self.ENDING_RATIONALITY
    
    def generate_final_dossier(self) -> Dict[str, Any]:
        """
        Generate comprehensive end-of-game report.
        
        Returns:
            Dictionary containing all final state data
        """
        ending = self.calculate_ending_path()
        
        # Get final stats
        sanity = self.player_state.get("sanity", 0)
        reality = self.player_state.get("reality", 0)
        
        # Get theory resolution
        proven_theories = self.board.get_proven_theories()
        resolution = self.board.get_resolution_summary()
        
        # Get key skills
        key_skills = {}
        for skill_name in ["Logic", "Subconscious", "Empathy", "Fortitude", "Skepticism"]:
            skill = self.skill_system.get_skill(skill_name)
            if skill:
                key_skills[skill_name] = skill.effective_level
        
        # Phase 7: Comprehensive skill usage statistics
        skill_usage_stats = self._calculate_skill_usage()
        argument_record = self._calculate_argument_record()
        
        # Get memories
        memories_unlocked = self.player_state.get("suppressed_memories_unlocked", [])
        
        # Get critical choices
        critical_choices = self.player_state.get("critical_choices", [])
        
        # Phase 7: Evidence and timeline
        evidence_stats = self._calculate_evidence_stats()
        timeline = self._generate_timeline()
        relationship_web = self._generate_relationship_web()
        
        dossier = {
            "ending_path": ending,
            "trigger_reason": self.trigger_reason,
            "timestamp": datetime.now().isoformat(),
            
            "final_stats": {
                "sanity": sanity,
                "reality": reality,
                "moral_corruption": self.player_state.get("moral_corruption_score", 0)
            },
            
            "theories": {
                "proven": proven_theories,
                "proven_count": resolution["proven"],
                "disproven_count": resolution["disproven"],
                "unresolved_count": resolution["unresolved"]
            },
            
            "skills": key_skills,
            
            # Phase 7: Enhanced statistics
            "skill_usage": skill_usage_stats,
            "argument_record": argument_record,
            "evidence": evidence_stats,
            "timeline": timeline,
            "relationships": relationship_web,
            
            "memories_unlocked": memories_unlocked,
            "memories_count": len(memories_unlocked),
            
            "critical_choices": critical_choices,
            
            "injuries": self.player_state.get("injuries", []),
            
            "playtime": self.player_state.get("playtime_minutes", 0)
        }
        
        return dossier
    
    def _calculate_skill_usage(self) -> Dict[str, Any]:
        """Calculate which skills were used most frequently."""
        check_history = self.skill_system.check_history
        skill_counts = {}
        
        for check_id, result in check_history.items():
            skill = result.get("skill")
            if skill:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Sort by usage
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_checks": len(check_history),
            "most_used": sorted_skills[:5] if sorted_skills else [],
            "by_skill": skill_counts
        }
    
    def _calculate_argument_record(self) -> Dict[str, Any]:
        """Calculate win/loss record for skill arguments."""
        # This would require tracking arguments in player_state
        # For now, return placeholder structure
        return {
            "total_arguments": 0,
            "sided_with": {},
            "suppressed_skills": []
        }
    
    def _calculate_evidence_stats(self) -> Dict[str, Any]:
        """Calculate evidence collection statistics."""
        # This would require access to inventory_system
        # For now, return placeholder
        return {
            "total_collected": 0,
            "analyzed": 0,
            "degraded": 0
        }
    
    def _generate_timeline(self) -> List[Dict[str, str]]:
        """Generate timeline of major events."""
        # This would require event tracking in player_state
        # For now, return placeholder
        return [
            {"time": "Day 1", "event": "Arrived in Kaltvik"},
            {"time": "Day 3", "event": "First theory internalized"}
        ]
    
    def _generate_relationship_web(self) -> Dict[str, Any]:
        """Generate relationship web showing NPC connections."""
        # This would require NPC tracking
        # For now, return placeholder
        return {
            "npcs_met": [],
            "trust_levels": {},
            "key_relationships": []
        }
    
    def export_dossier(self, dossier: Dict[str, Any], output_dir: str = "dossiers") -> str:
        """
        Export final dossier to JSON file.
        
        Returns:
            Path to exported file
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dossier_final_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dossier, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def run_ending_sequence(self, printer=print):
        """Execute the final ending sequence based on determined path."""
        ending = self.calculate_ending_path()
        self.ending_path = ending
        
        printer("\n" + "#"*60)
        printer("#" + " "*58 + "#")
        printer(f"#  FINAL ACT: {ending.upper():^50}  #")
        printer("#" + " "*58 + "#")
        printer("#"*60 + "\n")
        
        # Display ending narrative
        self._display_ending_narrative(ending, printer)
        
        # Generate and export dossier
        dossier = self.generate_final_dossier()
        filepath = self.export_dossier(dossier)
        
        printer("\n" + "="*60)
        printer("  FINAL DOSSIER")
        printer("="*60)
        printer(f"Ending: {ending.upper()}")
        printer(f"Final Sanity: {dossier['final_stats']['sanity']:.1f}")
        printer(f"Final Reality: {dossier['final_stats']['reality']:.1f}")
        printer(f"Theories Proven: {dossier['theories']['proven_count']}")
        printer(f"Memories Unlocked: {dossier['memories_count']}")
        printer(f"Moral Corruption: {dossier['final_stats']['moral_corruption']}")
        printer("="*60)
        printer(f"\nFull dossier exported to: {filepath}")
        printer("\nThank you for playing Tyger Tyger Liar Liar.\n")
    
    def _display_ending_narrative(self, ending: str, printer=print):
        """Display the narrative text for a specific ending."""
        narratives = {
            self.ENDING_COLLAPSE: [
                "The boundaries dissolve.",
                "You are no longer sure where the town ends and you begin.",
                "Faces merge. Time loops. The Tyger burns too bright.",
                "",
                "There is no you. There never was.",
                "",
                "[ENDING: IDENTITY DEATH]"
            ],
            
            self.ENDING_RATIONALITY: [
                "You pack your bags. The report is filed.",
                "Mass hysteria. Shared delusion. Perfectly explainable.",
                "",
                "You leave Tyger Tyger behind.",
                "But the silence follows you.",
                "",
                "[ENDING: COLD CASE]"
            ],
            
            self.ENDING_CONSPIRACY: [
                "You know the truth now.",
                "They are watching. They know that you know.",
                "",
                "You run, but you cannot hide from what is ancient.",
                "The Tyger sees all.",
                "",
                "[ENDING: THE TRUTH IS OUT THERE]"
            ],
            
            self.ENDING_CORRUPTION: [
                "You solved it. You won.",
                "But looking in the mirror, you don't recognize the eyes staring back.",
                "",
                "Necessary sacrifices, you tell yourself.",
                "The ends justified the means.",
                "",
                "Didn't they?",
                "",
                "[ENDING: PYRRHIC VICTORY]"
            ],
            
            self.ENDING_REDEMPTION: [
                "The horror is real, but so is the healing.",
                "You stand firm against the dark.",
                "",
                "You may not save everyone.",
                "But you saved yourself.",
                "",
                "And that's a start.",
                "",
                "[ENDING: DAWN]"
            ]
        }
        
        lines = narratives.get(ending, ["[UNKNOWN ENDING]"])
        for line in lines:
            printer(line)
            # Only sleep if we are using the default print (interactive mode assumption)
            if line and printer == print:  
                import time
                time.sleep(0.5)
