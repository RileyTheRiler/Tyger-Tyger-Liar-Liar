"""
Test script for Week 6 Journal and Evidence System
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from journal_system import JournalManager
from inventory_system import Evidence, InventoryManager
import json

def test_journal_entries():
    """Test journal entry creation and display."""
    print("\n=== Testing Journal Entries ===")
    journal = JournalManager()
    
    journal.add_entry(
        title="Found Blood Sample",
        body="Collected blood sample under porch. Forensics needed.",
        tags=["evidence", "forensics"]
    )
    
    journal.add_entry(
        title="Interview with Dr. Keats",
        body="Dr. Keats seemed nervous when discussing the woods.",
        tags=["interview", "suspicious"]
    )
    
    assert len(journal.entries) == 2, "Should have 2 entries"
    print("✓ Journal entries test PASSED")

def test_evidence_enhancement():
    """Test enhanced Evidence class with analysis."""
    print("\n=== Testing Enhanced Evidence ===")
    
    evidence = Evidence(
        id="bloody_shard",
        name="Bloody Glass Shard",
        description="A jagged piece of glass with dried blood.",
        type="physical",
        location="porch",
        related_skills=["Forensics", "Pattern Recognition"],
        analyzed=False,
        related_npcs=["Dr. Keats"]
    )
    
    assert evidence.name == "Bloody Glass Shard"
    assert not evidence.analyzed
    assert "Forensics" in evidence.related_skills
    
    # Test analysis
    evidence.analyze_with_skill("Forensics", "Blood type matches victim")
    assert evidence.analyzed
    assert "Forensics" in evidence.analysis_results
    
    print("✓ Evidence enhancement test PASSED")

def test_evidence_loading():
    """Test loading evidence from JSON."""
    print("\n=== Testing Evidence Loading ===")
    
    if not os.path.exists("data/evidence.json"):
        print("⚠ evidence.json not found, skipping test")
        return
    
    with open("data/evidence.json", "r") as f:
        evidence_data = json.load(f)
    
    inventory = InventoryManager()
    
    for ev_data in evidence_data:
        evidence = Evidence.from_dict(ev_data)
        inventory.add_evidence(evidence)
    
    assert len(inventory.evidence_collection) == len(evidence_data)
    assert "bloody_shard" in inventory.evidence_collection
    
    print(f"✓ Loaded {len(evidence_data)} evidence items")

def test_journal_leads():
    """Test lead tracking."""
    print("\n=== Testing Lead Tracking ===")
    journal = JournalManager()
    
    journal.add_lead("What happened in the woods on October 13?")
    journal.add_lead("Why is Dr. Keats lying?")
    
    assert len(journal.leads) == 2
    print("✓ Lead tracking test PASSED")

def test_suspect_tracking():
    """Test suspect/NPC tracking."""
    print("\n=== Testing Suspect Tracking ===")
    journal = JournalManager()
    
    journal.add_suspect({
        "id": "dr_keats",
        "name": "Dr. Marcus Keats",
        "age": 45,
        "role": "Local Physician",
        "notes": "Nervous, evasive about the woods",
        "status": "Active"
    })
    
    journal.update_suspect_status("dr_keats", "Suspicious")
    journal.add_suspect_flag("dr_keats", "Deceptive")
    journal.link_evidence_to_suspect("dr_keats", "bloody_shard")
    
    assert journal.suspects["dr_keats"].status == "Suspicious"
    assert "Deceptive" in journal.suspects["dr_keats"].flags
    assert "bloody_shard" in journal.suspects["dr_keats"].evidence_links
    
    print("✓ Suspect tracking test PASSED")

def test_serialization():
    """Test journal state export/import."""
    print("\n=== Testing Serialization ===")
    journal1 = JournalManager()
    
    journal1.add_entry("Test Entry", "Test body", ["test"])
    journal1.add_lead("Test lead")
    
    # Export
    state = journal1.export_state()
    
    # Import to new journal
    journal2 = JournalManager()
    journal2.load_state(state)
    
    assert len(journal2.entries) == 1
    assert len(journal2.leads) == 1
    assert journal2.entries[0].title == "Test Entry"
    
    print("✓ Serialization test PASSED")

def main():
    print("="*60)
    print("Week 6 Journal & Evidence System Test Suite")
    print("="*60)
    
    try:
        test_journal_entries()
        test_evidence_enhancement()
        test_evidence_loading()
        test_journal_leads()
        test_suspect_tracking()
        test_serialization()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
