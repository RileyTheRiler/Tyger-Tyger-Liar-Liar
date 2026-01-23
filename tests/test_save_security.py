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
        # Create a temporary directory for saves and exports
        save_dir = os.path.join(os.path.dirname(__file__), "temp_saves_security")
        export_dir = os.path.join(os.path.dirname(__file__), "temp_exports_security")

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

    def test_export_traversal_prevention(self, save_system):
        """Test that export_save prevents path traversal."""
        # Create a dummy save to export
        save_system.save_game("test_slot", {"data": "test"})

        # Payload trying to write outside exports dir
        payloads = [
            "../evil.txt",
            "/tmp/evil.txt",
            "foo/bar.json"
        ]

        for payload in payloads:
            success = save_system.export_save("test_slot", payload)
            assert success is False, f"Should reject export payload: {payload}"

    def test_valid_export(self, save_system):
        """Test that valid export works and writes to export directory."""
        save_system.save_game("test_slot", {"data": "test"})

        success = save_system.export_save("test_slot", "safe_export.json")
        assert success is True

        expected_path = os.path.join(save_system.export_directory, "safe_export.json")
        assert os.path.exists(expected_path)
