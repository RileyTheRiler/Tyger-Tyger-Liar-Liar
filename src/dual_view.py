"""
Dual View System - Split-screen narrative display.
Shows both Believer and Skeptic interpretations simultaneously.
"""

from typing import Dict, Optional
import textwrap

class DualView:
    """Renders split-screen narrative showing both worldview perspectives."""
    
    @staticmethod
    def render(believer_text: str, skeptic_text: str, title: str = "DUAL PERSPECTIVE") -> str:
        """
        Creates a split-screen ASCII display with believer on left, skeptic on right.
        
        Args:
            believer_text: Text for believer perspective
            skeptic_text: Text for skeptic perspective
            title: Optional title for the display
            
        Returns:
            Formatted split-screen string
        """
        width = 60
        col_width = 27  # Each column width
        
        # Wrap text to fit columns
        believer_lines = textwrap.wrap(believer_text, width=col_width)
        skeptic_lines = textwrap.wrap(skeptic_text, width=col_width)
        
        # Pad to same length
        max_lines = max(len(believer_lines), len(skeptic_lines))
        while len(believer_lines) < max_lines:
            believer_lines.append("")
        while len(skeptic_lines) < max_lines:
            skeptic_lines.append("")
        
        # Build output
        lines = []
        lines.append("╔" + "═" * width + "╗")
        lines.append("║" + title.center(width) + "║")
        lines.append("╠" + "═" * col_width + "╦" + "═" * col_width + "═╣")
        lines.append("║" + "BELIEVER PERSPECTIVE".center(col_width) + "║" + "SKEPTIC PERSPECTIVE".center(col_width) + " ║")
        lines.append("╠" + "═" * col_width + "╬" + "═" * col_width + "═╣")
        
        for b_line, s_line in zip(believer_lines, skeptic_lines):
            lines.append("║ " + b_line.ljust(col_width - 1) + "║ " + s_line.ljust(col_width - 1) + "║")
        
        lines.append("╚" + "═" * col_width + "╩" + "═" * col_width + "═╝")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_compact(believer_text: str, skeptic_text: str) -> str:
        """
        Simpler side-by-side display without heavy borders.
        """
        col_width = 35
        
        believer_lines = textwrap.wrap(believer_text, width=col_width)
        skeptic_lines = textwrap.wrap(skeptic_text, width=col_width)
        
        max_lines = max(len(believer_lines), len(skeptic_lines))
        while len(believer_lines) < max_lines:
            believer_lines.append("")
        while len(skeptic_lines) < max_lines:
            skeptic_lines.append("")
        
        lines = []
        lines.append("[BELIEVER]".ljust(col_width + 2) + "[SKEPTIC]")
        lines.append("-" * 72)
        
        for b_line, s_line in zip(believer_lines, skeptic_lines):
            lines.append(b_line.ljust(col_width + 2) + s_line)
        
        return "\n".join(lines)


def demo_dual_view():
    """Test the dual view rendering."""
    believer = "The lights descend deliberately, hunting. You can FEEL its attention on you. This is no natural phenomenon—it's alive, aware, and it knows you're here."
    
    skeptic = "Atmospheric refraction creates the illusion of movement. Your elevated heart rate is adrenaline response to unfamiliar stimuli. The aurora follows predictable electromagnetic patterns."
    
    print("\n" + "=" * 60)
    print("DUAL VIEW DEMO")
    print("=" * 60)
    
    print("\n[FULL RENDER]")
    print(DualView.render(believer, skeptic, "FIRST AURORA ENCOUNTER"))
    
    print("\n[COMPACT RENDER]")
    print(DualView.render_compact(believer, skeptic))
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo_dual_view()
