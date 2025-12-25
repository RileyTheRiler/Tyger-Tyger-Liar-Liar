
import pytest
import os
import shutil
from src.engine.case_file_system import CaseFileSystem, CaseFile, Evidence
from src.engine.board import Board, Theory

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

def test_case_creation(clean_case_system):
    case = clean_case_system.create_case("case_001", "Missing Person", "Find Alice")
    assert case.id == "case_001"
    assert case.title == "Missing Person"
    assert clean_case_system.get_case("case_001") == case

def test_evidence_linking(clean_case_system):
    case = clean_case_system.create_case("case_001", "Missing Person", "Find Alice")
    ev = Evidence("ev_01", "Bloody Scarf", "Found in woods", "physical", "clean", "case_001")

    clean_case_system.add_evidence(ev)

    assert "ev_01" in case.evidence_ids
    assert clean_case_system.get_evidence("ev_01") == ev

def test_timeline_event(clean_case_system):
    case = clean_case_system.create_case("case_001", "Missing Person", "Find Alice")
    clean_case_system.add_timeline_event("case_001", "2023-10-27 10:00", "Alice seen at bus stop")

    assert len(case.timeline) == 1
    assert case.timeline[0]["description"] == "Alice seen at bus stop"

def test_board_evolution():
    # Mock Theory Data
    import src.engine.board
    src.engine.board.THEORY_DATA = {
        "theory_base": {
            "name": "Base Theory",
            "category": "Test",
            "description": "Base",
            "evolves_into": "theory_evolved",
            "evolution_threshold": 2,
            "status": "active"
        },
        "theory_evolved": {
            "name": "Evolved Theory",
            "category": "Test",
            "description": "Evolved",
            "status": "available"
        }
    }

    board = Board()
    t_base = board.get_theory("theory_base")
    assert t_base.status == "active"

    # Add evidence 1
    res = board.add_evidence_to_theory("theory_base", "ev1")
    assert res["success"]
    assert not res["evolved"]
    assert t_base.evidence_count == 1

    # Add evidence 2 (Threshold met)
    res = board.add_evidence_to_theory("theory_base", "ev2")
    assert res["success"]
    assert res["evolved"]
    assert res["new_theory"] == "Evolved Theory"

    # Check states
    assert t_base.status == "closed"
    assert t_base.proven == True

    t_evolved = board.get_theory("theory_evolved")
    assert t_evolved.status == "active"

def test_board_degradation():
    import src.engine.board
    src.engine.board.THEORY_DATA = {
        "theory_fragile": {
            "name": "Fragile Theory",
            "category": "Test",
            "description": "Weak",
            "degradation_rate": 50,
            "status": "active"
        }
    }

    board = Board()
    t = board.get_theory("theory_fragile")

    # Hit 1
    res = board.add_contradiction_to_theory("theory_fragile", "contra1")
    assert res["success"]
    assert t.health == 50.0
    assert not res["theory_collapsed"]

    # Hit 2 (Collapse)
    res = board.add_contradiction_to_theory("theory_fragile", "contra2")
    assert res["success"]
    assert t.health == 0.0
    assert res["theory_collapsed"]
    assert t.status == "closed"
    assert t.proven == False
