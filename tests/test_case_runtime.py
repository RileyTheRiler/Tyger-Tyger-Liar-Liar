
import pytest
import os
from src.engine.case_file_system import CaseFileSystem, CaseFile, Evidence

@pytest.fixture
def clean_case_system():
    # Setup
    test_file = "data/test_cases.json"
    if os.path.exists(test_file):
        os.remove(test_file)

    # Run
    system = CaseFileSystem(data_path=test_file)
    yield system

    # Teardown
    if os.path.exists(test_file):
        os.remove(test_file)

def test_evidence_discovery(clean_case_system):
    # Setup
    case = clean_case_system.create_case("c1", "Test", "Desc")
    ev = Evidence("ev1", "Item", "Desc", "phys", "clean", "c1")
    clean_case_system.add_evidence(ev)

    # Assert initially hidden
    assert not clean_case_system.is_evidence_discovered("ev1")

    # Discover
    assert clean_case_system.discover_evidence("ev1")
    assert clean_case_system.is_evidence_discovered("ev1")

    # Re-discover returns false (no change)
    assert not clean_case_system.discover_evidence("ev1")

def test_suspect_discovery(clean_case_system):
    clean_case_system.create_case("c1", "Test", "Desc")

    clean_case_system.discover_suspect("c1", "npc_jim")

    state = clean_case_system.get_player_case_state()
    assert "npc_jim" in state["discovered_suspects"]["c1"]

def test_persistence(clean_case_system):
    clean_case_system.create_case("c1", "Test", "Desc")
    clean_case_system.add_evidence(Evidence("ev1", "Item", "Desc", "phys", "clean", "c1"))

    clean_case_system.discover_evidence("ev1")

    state = clean_case_system.get_player_case_state()

    # New system instance simulating load
    new_system = CaseFileSystem(data_path=clean_case_system.data_path)
    new_system.load_player_case_state(state)

    assert new_system.is_evidence_discovered("ev1")
