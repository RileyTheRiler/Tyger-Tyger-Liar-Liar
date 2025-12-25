"""
Visual Board UI - ASCII art representation of The Board system.
Displays active theories, their health, connections, and evidence links.
"""

from typing import Dict, List
from board import Board, Theory


class BoardUI:
    """Renders The Board as ASCII art."""
    
    def __init__(self, board: Board):
        self.board = board
        
    def render(self) -> str:
        """Generate full ASCII board display."""
        lines = []
        
        # Header
        lines.append("╔═══════════════════════════════════════════════════════════╗")
        lines.append("║                      THE BOARD                            ║")
        lines.append("╠═══════════════════════════════════════════════════════════╣")
        lines.append("║                                                           ║")
        
        # Get theories by status
        active_theories = []
        internalizing_theories = []
        degraded_theories = []
        
        for theory_id, theory in self.board.theories.items():
            if theory.status == "active":
                if theory.health < 50:
                    degraded_theories.append(theory)
                else:
                    active_theories.append(theory)
            elif theory.status == "internalizing":
                internalizing_theories.append(theory)
        
        # Display active theories
        for theory in active_theories:
            lines.extend(self._render_theory(theory, "ACTIVE"))
        
        # Display degraded theories
        for theory in degraded_theories:
            lines.extend(self._render_theory(theory, "DEGRADED"))
        
        # Display internalizing theories
        for theory in internalizing_theories:
            lines.extend(self._render_theory(theory, "INTERNALIZING"))
        
        # Show conflicts
        if len(active_theories) > 1 or (active_theories and internalizing_theories):
            lines.append("║                                                           ║")
            lines.append("║  CONFLICTS:                                               ║")
            for theory in active_theories + internalizing_theories:
                if theory.conflicts_with:
                    conflict_names = [self.board.get_theory(cid).name for cid in theory.conflicts_with 
                                    if self.board.get_theory(cid)]
                    if conflict_names:
                        lines.append(f"║    '{theory.name}' ⚔ {', '.join(conflict_names[:2])}...")
        
        if not active_theories and not internalizing_theories and not degraded_theories:
            lines.append("║  No theories currently internalized.                      ║")
            lines.append("║                                                           ║")
        
        # Footer
        lines.append("║                                                           ║")
        lines.append("╚═══════════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def _render_theory(self, theory: Theory, status_label: str) -> List[str]:
        """Render a single theory entry."""
        lines = []
        
        # Status indicator with color
        if status_label == "ACTIVE":
            indicator = "●"  # Green in terminal
        elif status_label == "DEGRADED":
            indicator = "◐"  # Orange/yellow
        elif status_label == "INTERNALIZING":
            indicator = "○"  # White/hollow
        else:
            indicator = "◌"
        
        # Theory name and status
        theory_line = f"║  [{status_label}] {indicator} {theory.name}"
        # Pad to 59 chars (61 - 2 for borders)
        theory_line = theory_line.ljust(61) + "║"
        lines.append(theory_line)
        
        # Health bar (if active or degraded)
        if theory.status in ["active", "internalizing"]:
            health_bar = self._create_health_bar(theory.health)
            lines.append(f"║    Health: {health_bar} {int(theory.health)}%".ljust(61) + "║")
        
        # Evidence and contradictions
        if theory.evidence_count > 0 or theory.contradictions > 0:
            evidence_line = f"║    Evidence: {theory.evidence_count} | Contradictions: {theory.contradictions}"
            lines.append(evidence_line.ljust(61) + "║")
        
        # Internalization progress
        if theory.status == "internalizing":
            required_minutes = theory.internalize_time_hours * 60
            progress_pct = (theory.internalization_progress_minutes / required_minutes) * 100
            progress_bar = self._create_progress_bar(progress_pct)
            hours_left = (required_minutes - theory.internalization_progress_minutes) / 60
            lines.append(f"║    Progress: {progress_bar} {hours_left:.1f}h remaining".ljust(61) + "║")
        
        # Proven status
        if theory.proven is not None:
            status_text = "PROVEN ✓" if theory.proven else "DISPROVEN ✗"
            lines.append(f"║    Status: {status_text}".ljust(61) + "║")
        
        lines.append("║                                                           ║")
        
        return lines
    
    def _create_health_bar(self, health: float) -> str:
        """Create a visual health bar."""
        bar_length = 20
        filled = int((health / 100) * bar_length)
        empty = bar_length - filled
        
        if health >= 80:
            fill_char = "█"
        elif health >= 50:
            fill_char = "▓"
        elif health >= 20:
            fill_char = "▒"
        else:
            fill_char = "░"
        
        return f"[{fill_char * filled}{'·' * empty}]"
    
    def _create_progress_bar(self, progress_pct: float) -> str:
        """Create a visual progress bar."""
        bar_length = 15
        filled = int((progress_pct / 100) * bar_length)
        empty = bar_length - filled
        return f"[{'█' * filled}{'·' * empty}]"
    
    def render_compact(self) -> str:
        """Render a compact single-line summary."""
        active_count = sum(1 for t in self.board.theories.values() if t.status == "active")
        internalizing_count = sum(1 for t in self.board.theories.values() if t.status == "internalizing")
        
        summary = f"[BOARD] Active: {active_count} | Internalizing: {internalizing_count}"
        
        # Show degraded theories
        degraded = [t for t in self.board.theories.values() 
                   if t.status == "active" and t.health < 50]
        if degraded:
            summary += f" | ⚠ {len(degraded)} degraded"
        
        return summary
    
    def render_theory_list(self, status_filter: str = None) -> str:
        """Render a simple list of theories by status."""
        lines = []
        lines.append("\n" + "=" * 60)
        lines.append("THEORY LIST")
        lines.append("=" * 60)
        
        statuses = ["active", "internalizing", "available", "locked", "closed"]
        if status_filter:
            statuses = [status_filter]
        
        for status in statuses:
            theories = [t for t in self.board.theories.values() if t.status == status]
            if theories:
                lines.append(f"\n{status.upper()}:")
                for theory in theories:
                    health_info = f" (Health: {int(theory.health)}%)" if status in ["active", "internalizing"] else ""
                    lines.append(f"  • {theory.name}{health_info}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


def demo_board_ui():
    """Demo function to show board UI in action."""
    from board import Board
    
    board = Board()
    ui = BoardUI(board)
    
    # Discover and internalize some theories
    board.discover_theory("i_want_to_believe")
    board.start_internalizing("i_want_to_believe")
    board.on_time_passed(360)  # Complete internalization
    
    board.discover_theory("trust_no_one")
    board.start_internalizing("trust_no_one")
    board.on_time_passed(120)  # Partial progress
    
    # Add some evidence and contradictions
    board.add_evidence_to_theory("i_want_to_believe", "aurora_footage")
    board.add_contradiction_to_theory("i_want_to_believe", "blood_analysis")
    board.add_contradiction_to_theory("i_want_to_believe", "witness_testimony")
    
    # Display the board
    print(ui.render())
    print("\n")
    print(ui.render_compact())
    print(ui.render_theory_list())


if __name__ == "__main__":
    demo_board_ui()
