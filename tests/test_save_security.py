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
        # Create temporary directories
        base_dir = os.path.dirname(__file__)
        save_dir = os.path.join(base_dir, "temp_saves_security")
        export_dir = os.path.join(base_dir, "temp_exports_security")

        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)
        if os.path.exists(export_dir):
            shutil.rmtree(export_dir)

        # Initialize with both directories
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

    def test_export_traversal_prevention(self, save_system):
        """Test that export path traversal is prevented."""
        # Setup a valid save to export
        save_system.save_game("test_slot", {"data": "secure"})

        payloads = [
            "../outside.json",
            "../../etc/passwd",
            "/absolute/path/test.json",
            "folder/test.json"
        ]

        for payload in payloads:
            success = save_system.export_save("test_slot", payload)
            assert success is False, f"Should reject invalid export filename: {payload}"

    def test_export_valid_filename(self, save_system):
        """Test that valid export filenames work and write to export directory."""
        save_system.save_game("test_slot", {"data": "secure"})

        filename = "valid_export.json"
        success = save_system.export_save("test_slot", filename)
        assert success is True, "Export should succeed"

        expected_path = os.path.join(save_system.export_directory, filename)
        assert os.path.exists(expected_path), f"File should be created in export dir: {expected_path}"
