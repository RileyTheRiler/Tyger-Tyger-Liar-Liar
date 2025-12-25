from engine.input_handler import get_player_input, parse_command
from utils.formatter import highlight_objects
import io
import sys

def test_highlighting():
    print("Testing Highlighting...")
    text = "You stand at the edge of Kaltvik. A pale aurora stirs overhead."
    objects = {
        "kaltvik": "A remote Alaskan settlement.",
        "aurora": "Beautiful colors."
    }
    highlighted = highlight_objects(text, objects)
    print(f"Result: {highlighted}")
    assert "**kaltvik**" in highlighted.lower()
    assert "**aurora**" in highlighted.lower()
    print("Highlighting Test Passed!\n")

def test_parser():
    print("Testing Parser...")
    objects = {"kaltvik": "desc", "aurora": "desc"}
    
    # Test choice
    # Mocking input is tricky, let's test parse_command directly
    assert parse_command("1", objects) == ("invalid", None) # parse_command doesn't handle digits, get_player_input does
    
    # Test examine
    res = parse_command("examine kaltvik", objects)
    print(f"Examine Result: {res}")
    assert res == ("examine", "kaltvik")
    
    # Test look at
    res = parse_command("look at aurora", objects)
    print(f"Look At Result: {res}")
    assert res == ("examine", "aurora")
    
    # Test unknown
    res = parse_command("dance", objects)
    print(f"Unknown Result: {res}")
    assert res == ("invalid", None)
    
    print("Parser Test Passed!\n")

def test_input_handler():
    print("Testing Input Handler...")
    scene = {"options": [{"label": "Opt 1", "next": "next_scene"}]}
    objects = {"kaltvik": "desc"}
    
    # Test Digit Choice
    from unittest.mock import patch
    with patch('builtins.input', return_value='1'):
        res = get_player_input(scene, objects)
        print(f"Choice 1 Result: {res}")
        assert res == ("choice", 0)
        
    # Test Invalid Digit
    with patch('builtins.input', return_value='5'):
        res = get_player_input(scene, objects)
        print(f"Choice 5 Result: {res}")
        assert res == ("invalid", None)
        
    # Test Parser through get_player_input
    with patch('builtins.input', return_value='examine kaltvik'):
        res = get_player_input(scene, objects)
        print(f"Examine Result: {res}")
        assert res == ("examine", "kaltvik")

    print("Input Handler Test Passed!\n")

if __name__ == "__main__":
    from engine.input_handler import get_player_input
    test_highlighting()
    test_parser()
    test_input_handler()
