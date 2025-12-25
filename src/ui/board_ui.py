"""
Visual Board UI - ASCII art representation of The Board system.
Displays active theories, their health, connections, and evidence links.
"""

from typing import Dict, List
from board import Board, Theory
from interface import Colors


class BoardUI:
    """Renders The Board as ASCII art."""
    
    def __init__(self, board: Board):
        self.board = board
        
    def render(self) -> str:
        """Generate full ASCII board display."""
        lines = []
        
        # Header
        lines.append(f"{Colors.CYAN}╔═══════════════════════════════════════════════════════════╗")
        lines.append(f"║                      {Colors.BOLD}THE BOARD{Colors.RESET}{Colors.CYAN}                            ║")
        lines.append("╠═══════════════════════════════════════════════════════════╣")
        lines.append(f"║                                                           ║{Colors.RESET}")
        
        # Get theories by status
        active_theories = []
        internalizing_theories = []
        degraded_theories = []
        closed_theories = [] # New: Show closed theories?
        
        for theory_id, theory in self.board.theories.items():
            if theory.status == "active":
                if theory.health < 50:
                    degraded_theories.append(theory)
                else:
                    active_theories.append(theory)
            elif theory.status == "internalizing":
                internalizing_theories.append(theory)
            elif theory.status == "closed":
                 closed_theories.append(theory)
        
        # Display active theories
        for theory in active_theories:
            lines.extend(self._render_theory(theory, "ACTIVE"))
        
        # Display degraded theories
        for theory in degraded_theories:
            lines.extend(self._render_theory(theory, "DEGRADED"))
        
        # Display internalizing theories
        for theory in internalizing_theories:
            lines.extend(self._render_theory(theory, "INTERNALIZING"))

        # Display closed (evolution/collapse) - Limited to recent?
        # For now, show them if they have significant data
        for theory in closed_theories:
             if theory.proven is not None:
                 status = "PROVEN" if theory.proven else "DISPROVEN"
                 lines.extend(self._render_theory(theory, status))
        
        # Show conflicts
        if len(active_theories) > 1 or (active_theories and internalizing_theories):
            lines.append(f"{Colors.CYAN}║                                                           ║")
            lines.append(f"║  {Colors.RED}CONFLICTS:{Colors.CYAN}                                               ║")
            for theory in active_theories + internalizing_theories:
                if theory.conflicts_with:
                    conflict_names = [self.board.get_theory(cid).name for cid in theory.conflicts_with 
                                    if self.board.get_theory(cid)]
                    if conflict_names:
                        # Need to handle length carefully with colors
                        base = f"║    '{theory.name}' ⚔ {', '.join(conflict_names[:2])}..."
                        print_len = len(base)
                        padding = 61 - print_len
                        if padding < 0:
                             # Truncate string if too long
                             truncated = f"'{theory.name}' ⚔ {', '.join(conflict_names[:2])}..."[:58]
                             lines.append(f"{Colors.CYAN}║    {Colors.RED}{truncated}{Colors.CYAN}║")
                        else:
                             lines.append(f"{Colors.CYAN}║    {Colors.RED}'{theory.name}' ⚔ {', '.join(conflict_names[:2])}...{Colors.CYAN}" + " " * padding + "║")
        
        if not active_theories and not internalizing_theories and not degraded_theories:
            lines.append(f"{Colors.CYAN}║  {Colors.WHITE}No theories currently internalized.{Colors.CYAN}                      ║")
            lines.append(f"║                                                           ║{Colors.RESET}")
        
        # Footer
        lines.append(f"{Colors.CYAN}║                                                           ║")
        lines.append(f"╚═══════════════════════════════════════════════════════════╝{Colors.RESET}")
        
        return "\n".join(lines)
    
    def _render_theory(self, theory: Theory, status_label: str) -> List[str]:
        """Render a single theory entry."""
        lines = []
        
        # Status indicator with color
        color = Colors.WHITE
        if status_label == "ACTIVE":
            indicator = "●"
            color = Colors.GREEN
        elif status_label == "DEGRADED":
            indicator = "◐"
            color = Colors.YELLOW
        elif status_label == "INTERNALIZING":
            indicator = "○"
            color = Colors.BLUE
        elif status_label == "PROVEN":
            indicator = "✓"
            color = Colors.CYAN
        elif status_label == "DISPROVEN":
            indicator = "✗"
            color = Colors.RED
        else:
            indicator = "◌"
        
        # Theory name and status
        # We construct the visible string to calculate padding, then inject colors
        # Visible area inside borders is 59 chars.
        # Format: "║  [STATUS] I Name"
        # Prefix length
        prefix = f"║  [{status_label}] {indicator} "
        available_width = 59 - len(prefix) + 1 # +1 for the ║ char count confusion in previous logic?
        # Actually board width is 61 (61 chars from ╔ to ╗ inclusive? No.)
        # Top line: ╔ + 59 chars + ╗ = 61 chars wide total.
        # Inner width is 59 chars.

        # Calculate available space for name
        # "║  " = 3 chars
        # "[STATUS] " = len(status_label) + 3 chars
        # "I " = 2 chars
        # Total prefix len = 3 + len(status_label) + 3 + 2 = 8 + len(status_label)

        display_name = theory.name
        visible_prefix_len = len(f"║  [{status_label}] {indicator} ")
        max_name_len = 59 - visible_prefix_len + 1 # +1 accounting for border index 0?
        # Let's trust the padding logic: padding = 61 - len(visible_part)
        # We want padding >= 0, so len(visible_part) <= 61.
        # Wait, the string ends with "║", so visible_part + padding + "║" = 61 chars?
        # Standard line: "║" + 59 spaces + "║" -> len 61.
        # visible_part includes the starting "║".

        prefix_str = f"║  [{status_label}] {indicator} "
        max_name_len = 61 - len(prefix_str) - 1 # -1 for right border

        if len(display_name) > max_name_len:
            display_name = display_name[:max_name_len-3] + "..."

        visible_part = f"{prefix_str}{display_name}"
        padding = 61 - len(visible_part) - 1 # -1 because we add the right border manually

        theory_line = f"{Colors.CYAN}║  {color}[{status_label}] {indicator} {display_name}{Colors.CYAN}" + " " * padding + "║"
        lines.append(theory_line)
        
        # Health bar (if active or degraded)
        if theory.status in ["active", "internalizing", "closed"]:
             # Show health even if closed (as 0 or final state)
            health_bar = self._create_health_bar(theory.health)
            raw = f"║    Health: {health_bar} {int(theory.health)}%"
            padding = 61 - len(raw)
            lines.append(f"{Colors.CYAN}║    {Colors.WHITE}Health: {color}{health_bar} {int(theory.health)}%{Colors.CYAN}" + " " * padding + "║")
        
        # Evidence and contradictions
        if theory.evidence_count > 0 or theory.contradictions > 0:
            raw = f"║    Evidence: {theory.evidence_count} | Contradictions: {theory.contradictions}"
            padding = 61 - len(raw)
            lines.append(f"{Colors.CYAN}║    {Colors.WHITE}Evidence: {Colors.GREEN}{theory.evidence_count}{Colors.WHITE} | Contradictions: {Colors.RED}{theory.contradictions}{Colors.CYAN}" + " " * padding + "║")
        
        # Evolution status
        if theory.evolves_into and theory.status == "closed" and theory.proven:
            raw = f"║    EVOLVED -> {theory.evolves_into}"
            padding = 61 - len(raw)
            lines.append(f"{Colors.CYAN}║    {Colors.MAGENTA}EVOLVED -> {theory.evolves_into}{Colors.CYAN}" + " " * padding + "║")

        # Internalization progress
        if theory.status == "internalizing":
            required_minutes = theory.internalize_time_hours * 60
            progress_pct = (theory.internalization_progress_minutes / required_minutes) * 100
            progress_bar = self._create_progress_bar(progress_pct)
            hours_left = max(0, (required_minutes - theory.internalization_progress_minutes) / 60)
            raw = f"║    Progress: {progress_bar} {hours_left:.1f}h remaining"
            padding = 61 - len(raw)
            lines.append(f"{Colors.CYAN}║    {Colors.WHITE}Progress: {Colors.BLUE}{progress_bar} {hours_left:.1f}h remaining{Colors.CYAN}" + " " * padding + "║")
        
        lines.append(f"{Colors.CYAN}║                                                           ║{Colors.RESET}")
        
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
    board.discover_theory("trust_no_one")
    board.start_internalizing("trust_no_one")
    board.on_time_passed(120)  # Partial progress
    
    # Add some evidence and contradictions
    board.add_evidence_to_theory("trust_no_one", "aurora_footage")
    board.add_contradiction_to_theory("trust_no_one", "blood_analysis")
    
    # Display the board
    print(ui.render())
    print("\n")
    print(ui.render_compact())
    print(ui.render_theory_list())


if __name__ == "__main__":
    demo_board_ui()
