import os
from datetime import datetime
from typing import Dict, List, Any

class PDFExporter:
    """
    Generates a PDF-ready HTML report for the Case Dossier and Board.
    This HTML can be printed to PDF by the user or browser.
    """

    def __init__(self, game_state: Dict[str, Any]):
        self.game_state = game_state
        self.player_state = game_state.get("player_state", {})
        self.board = game_state.get("board")
        self.inventory = game_state.get("inventory_system")
        self.time_system = game_state.get("time_system")

    def generate_report(self, output_path: str = "case_dossier.html"):
        """Generates the HTML report."""

        html_content = self._generate_html()

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"[EXPORT] Case Dossier generated at '{output_path}'")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to generate report: {e}")
            return False

    def _generate_html(self) -> str:
        current_time = self.time_system.get_time_string() if self.time_system else "Unknown Time"
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        sanity = self.player_state.get("sanity", 0)
        reality = self.player_state.get("reality", 0)

        active_theories = []
        if self.board:
            active_theories = [t for t in self.board.theories.values() if t.status == "active"]

        evidence_list = []
        if self.inventory:
            evidence_list = [e for e in self.inventory.evidence_collection.values()]

        css = """
        body { font-family: 'Courier New', monospace; background-color: #f4f4f4; color: #333; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: #fff; padding: 40px; border: 1px solid #ccc; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }
        h2 { border-bottom: 1px solid #666; margin-top: 30px; }
        .meta { text-align: right; font-size: 0.8em; color: #666; margin-bottom: 20px; }
        .stat-box { display: flex; justify-content: space-around; background: #eee; padding: 10px; margin-bottom: 20px; border: 1px solid #ddd; }
        .theory-card { border: 1px solid #333; padding: 15px; margin-bottom: 15px; background: #fafafa; }
        .evidence-item { margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px dotted #ccc; }
        .evidence-meta { font-size: 0.8em; color: #555; }
        .stamp { position: absolute; top: 20px; right: 20px; border: 3px solid red; color: red; padding: 5px 10px; font-weight: bold; transform: rotate(-10deg); opacity: 0.7; }
        @media print { body { background: none; } .container { box-shadow: none; border: none; } }
        """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Case Dossier - {date_str}</title>
            <style>{css}</style>
        </head>
        <body>
            <div class="container">
                <div class="stamp">CONFIDENTIAL</div>
                <h1>CASE DOSSIER</h1>
                <div class="meta">
                    Generated: {date_str}<br>
                    In-Game Time: {current_time}
                </div>

                <div class="stat-box">
                    <div><strong>SANITY:</strong> {sanity:.0f}%</div>
                    <div><strong>REALITY:</strong> {reality:.0f}%</div>
                    <div><strong>ARCHETYPE:</strong> {self.player_state.get('archetype', 'Neutral')}</div>
                </div>

                <h2>CURRENT THEORIES</h2>
                {self._render_theories(active_theories)}

                <h2>EVIDENCE COLLECTION</h2>
                {self._render_evidence(evidence_list)}

                <h2>NOTES</h2>
                <p>__________________________________________________________________________</p>
                <p>__________________________________________________________________________</p>
                <p>__________________________________________________________________________</p>
            </div>
        </body>
        </html>
        """
        return html

    def _render_theories(self, theories):
        if not theories:
            return "<p>No active theories.</p>"

        html = ""
        for t in theories:
            effects = ", ".join([f"{k} {'+' if v>0 else ''}{v}" for k, v in t.effects.items()])
            html += f"""
            <div class="theory-card">
                <h3>{t.name}</h3>
                <p>{t.description}</p>
                <p><strong>Effects:</strong> {effects}</p>
                <p><strong>Health:</strong> {t.health}% | <strong>Contradictions:</strong> {t.contradictions}</p>
            </div>
            """
        return html

    def _render_evidence(self, evidence_list):
        if not evidence_list:
            return "<p>No evidence collected.</p>"

        html = ""
        for e in evidence_list:
            html += f"""
            <div class="evidence-item">
                <strong>{e.name}</strong> ({e.type})
                <br>{e.description}
                <div class="evidence-meta">
                    Found: {e.location or 'Unknown'} | ID: {e.id}
                    {self._render_analysis(e)}
                </div>
            </div>
            """
        return html

    def _render_analysis(self, evidence):
        if not evidence.analyzed:
            return ""

        results = []
        for skill, res in evidence.analysis_results.items():
            results.append(f"[{skill}: {res}]")
        return "<br><strong>Analysis:</strong> " + " ".join(results)
