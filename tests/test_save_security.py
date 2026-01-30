import pytest
import sys
import os
import shutil

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from engine.save_system import SaveSystem

class TestSaveSecurity:

    @pytest.fixture
    def save_system(self):
        # Create a temporary directory for saves
        base_dir = os.path.dirname(__file__)
        save_dir = os.path.join(base_dir, "temp_saves_security")
        export_dir = os.path.join(base_dir, "temp_exports_security")

        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)
        if os.path.exists(export_dir):
            shutil.rmtree(export_dir)

        system = SaveSystem(save_directory=save_dir, export_directory=export_dir)
        yield system

        # Cleanup
        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)
        if os.path.exists(export_dir):
            shutil.rmtree(export_dir)

    def test_path_traversal_prevention(self, save_system):
        """Test that path traversal characters and invalid filenames are rejected."""
        payloads = [
            "../outside",
            "../../etc/passwd",
            "foo/bar",
            "foo\\bar",
            ".hidden",
            "with.dot",
            "null\0byte"
        ]

        data = {"test": "data"}

        for payload in payloads:
            # save_game catches exceptions and returns False
            success = save_system.save_game(payload, data)
            assert success is False, f"Should reject invalid payload: {payload}"

    def test_valid_save_slots(self, save_system):
        """Test that valid slots work correctly."""
        valid_slots = [
            "save1",
            "my_save",
            "save-game-2",
            "Level 5",
            "Session_ABC-123"
        ]

        data = {"test": "data"}

        for slot in valid_slots:
            success = save_system.save_game(slot, data)
            assert success is True, f"Should accept valid slot: {slot}"
            expected_path = os.path.join(save_system.save_directory, f"{slot}.json")
            assert os.path.exists(expected_path), f"File should exist: {expected_path}"

    def test_load_traversal_prevention(self, save_system):
        """Test that loading with traversal path fails safely."""
        # load_game should return None if file invalid or not found
        result = save_system.load_game("../outside")
        assert result is None

    def test_delete_traversal_prevention(self, save_system):
        """Test that delete with traversal path fails safely."""
        result = save_system.delete_save("../outside")
        assert result is False

    def test_export_path_traversal(self, save_system):
        """Test that export_save sanitizes paths and prevents traversal."""
        # 1. Create a valid save to export
        slot = "valid_save"
        save_system.save_game(slot, {"secret": "data"})

        # 2. Attempt to export with traversal
        # We try to write to a file "pwned.txt" in the parent of export dir (which is test dir)
        traversal_path = "../pwned.txt"

        success = save_system.export_save(slot, traversal_path)
        assert success is True, "Export should succeed but be sanitized"

        # 3. Verify file exists in EXPORT dir, not parent
        safe_path = os.path.join(save_system.export_directory, "pwned.txt")
        unsafe_path = os.path.join(os.path.dirname(save_system.export_directory), "pwned.txt")

        assert os.path.exists(safe_path), f"File should be created in export dir: {safe_path}"
        assert not os.path.exists(unsafe_path), f"File should NOT be created at unsafe path: {unsafe_path}"

        # Cleanup unsafe file if it somehow was created
        if os.path.exists(unsafe_path):
            os.remove(unsafe_path)
