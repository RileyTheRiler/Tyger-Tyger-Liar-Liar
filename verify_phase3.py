import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
sys.path.append(str(src_dir))
sys.path.append(str(src_dir / "engine"))

from game_state import GameState
from text_composer import TextComposer, Archetype

def verify_phase3():
    print("Verifying Phase 3: Text Composition Pipeline...")
    
    gs = GameState()
    gs.attributes["REASON"] = 4
    gs.skills["Forensics"] = 2  # Total Logic/Forensics = 6
    gs.apply_flag("met_stranger", True)
    gs.add_board_node({"id": "theory_1", "title": "The Ghost in the Machine"})
    
    composer = TextComposer(game_state=gs)
    
    test_scene = {
        "base": "The room is dimly lit.\n\nParagraph two starts here.\n\nParagraph three is the last.",
        "lens": {
            "believer": "The shadows seem to breathe with a life of their own."
        },
        "inserts": [
            {
                "id": "forensics_blood",
                "condition": {"skill_gte": {"Forensics": 5}},
                "text": "[Forensics Success] You spot a dry bloodstain.",
                "insert_at": "AFTER_PARAGRAPH:0"
            },
            {
                "id": "flag_insert",
                "condition": {"flag_set": "met_stranger"},
                "text": "[Flag Success] You remember the stranger's warning.",
                "insert_at": "AFTER_PARAGRAPH:1"
            },
            {
                "id": "theory_insert",
                "condition": {"theory_active": "theory_1"},
                "text": "[Theory Success] This reminds you of your theory.",
                "insert_at": "AFTER_LENS"
            }
        ]
    }
    
    print("\n--- Composing BELIEVER text ---")
    result = composer.compose(test_scene, Archetype.BELIEVER, gs)
    print(result.full_text)
    
    # Verifications
    if "[Forensics Success]" in result.full_text and "Paragraph two" in result.full_text.split("\n\n")[0]:
         print("\n[SUCCESS] AFTER_PARAGRAPH:0 insertion verified.")
    else:
         print("\n[FAILURE] AFTER_PARAGRAPH:0 insertion failed or condition check failed.")
         
    if "[Flag Success]" in result.full_text.split("\n\n")[1]:
         print("[SUCCESS] AFTER_PARAGRAPH:1 insertion verified.")
    else:
         print("[FAILURE] AFTER_PARAGRAPH:1 insertion failed.")

    if "[Theory Success]" in result.full_text:
         print("[SUCCESS] Theory condition check verified.")
    else:
         print("[FAILURE] Theory condition check failed.")

if __name__ == "__main__":
    verify_phase3()
