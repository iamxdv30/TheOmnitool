"""
Tests for Migration Scripts

Tests export_tool_access.py and import_tool_access.py functionality.

Run with:
    pytest tests/test_migration_scripts.py
    pytest tests/test_migration_scripts.py -v  # Verbose
    pytest tests/test_migration_scripts.py::test_export_import_roundtrip  # Specific test
"""

import pytest
import json
import os
import tempfile
from model import db, User, Tool, ToolAccess
from scripts.export_tool_access import export_tool_access
from scripts.import_tool_access import import_tool_access, load_export_file


class TestExportToolAccess:
    """Tests for export_tool_access.py"""

    def test_export_creates_valid_json(self, app, init_database, tmp_path):
        """Test that export creates a valid JSON file"""
        output_path = tmp_path / "test_export.json"

        with app.app_context():
            result_path = export_tool_access(
                environment='local',
                output_path=str(output_path)
            )

            assert output_path.exists()
            assert result_path == str(output_path)

            # Verify JSON is valid
            with open(output_path, 'r') as f:
                data = json.load(f)

            # Check structure
            assert 'export_metadata' in data
            assert 'tool_access' in data
            assert 'tools' in data

            # Check metadata
            metadata = data['export_metadata']
            assert metadata['environment'] == 'local'
            assert 'timestamp' in metadata
            assert 'version' in metadata
            assert 'total_users' in metadata
            assert 'total_grants' in metadata

    def test_export_captures_user_context(self, app, init_database, tmp_path):
        """Test that export includes username and email"""
        output_path = tmp_path / "test_export.json"

        with app.app_context():
            export_tool_access(environment='local', output_path=str(output_path))

            with open(output_path, 'r') as f:
                data = json.load(f)

            # Check that tool_access records have user context
            if data['tool_access']:
                first_grant = data['tool_access'][0]
                assert 'username' in first_grant
                assert 'email' in first_grant
                assert 'tool_name' in first_grant
                assert 'user_id' in first_grant

    def test_export_sorted_for_git_diff(self, app, init_database, tmp_path):
        """Test that export is sorted consistently"""
        output_path = tmp_path / "test_export.json"

        with app.app_context():
            export_tool_access(environment='local', output_path=str(output_path))

            with open(output_path, 'r') as f:
                data = json.load(f)

            # Check tool_access is sorted by username, then tool_name
            grants = data['tool_access']
            if len(grants) > 1:
                for i in range(len(grants) - 1):
                    current = (grants[i]['username'], grants[i]['tool_name'])
                    next_grant = (grants[i+1]['username'], grants[i+1]['tool_name'])
                    assert current <= next_grant, "Grants should be sorted"

            # Check tools are sorted by name
            tools = data['tools']
            if len(tools) > 1:
                tool_names = [t['name'] for t in tools]
                assert tool_names == sorted(tool_names), "Tools should be sorted by name"


class TestImportToolAccess:
    """Tests for import_tool_access.py"""

    def test_load_export_file_validates_structure(self, tmp_path):
        """Test that load_export_file validates JSON structure"""
        invalid_file = tmp_path / "invalid.json"

        # Missing required keys
        with open(invalid_file, 'w') as f:
            json.dump({"invalid": "structure"}, f)

        with pytest.raises(ValueError, match="missing.*key"):
            load_export_file(str(invalid_file))

    def test_import_merge_mode_preserves_existing(self, app, init_database, tmp_path):
        """Test that merge mode doesn't delete existing grants"""
        export_path = tmp_path / "test_export.json"

        with app.app_context():
            # Export current state
            export_tool_access(environment='local', output_path=str(export_path))

            # Add an extra grant manually
            user = User.query.first()
            extra_tool = Tool.query.first()
            extra_grant = ToolAccess(user_id=user.id, tool_name=extra_tool.name + "_EXTRA")

            # Create a temporary "extra tool" for testing
            temp_tool = Tool(
                name=extra_tool.name + "_EXTRA",
                description="Temporary tool",
                route="/temp",
                is_default=False,
                is_active=True
            )
            db.session.add(temp_tool)
            db.session.add(extra_grant)
            db.session.commit()

            original_count = ToolAccess.query.count()

            # Import (merge mode)
            stats = import_tool_access(
                source_path=str(export_path),
                mode='merge',
                dry_run=False
            )

            # Verify extra grant still exists
            assert ToolAccess.query.filter_by(tool_name=extra_tool.name + "_EXTRA").first() is not None

            # Count should be >= original (may be same if all grants already existed)
            assert ToolAccess.query.count() >= original_count - 1  # -1 for the temp grant we added

    def test_import_handles_missing_users(self, app, init_database, tmp_path):
        """Test that import skips grants for non-existent users"""
        export_path = tmp_path / "test_export.json"

        with app.app_context():
            # Create export with non-existent user
            export_data = {
                "export_metadata": {
                    "environment": "test",
                    "timestamp": "2026-01-12T00:00:00Z",
                    "version": "1.0.0",
                    "total_users": 1,
                    "total_grants": 1,
                    "total_tools": 1
                },
                "tool_access": [
                    {
                        "username": "ghost_user_does_not_exist",
                        "email": "ghost@example.com",
                        "tool_name": "Test Tool 1",
                        "user_id": 99999  # Non-existent ID
                    }
                ],
                "tools": [
                    {
                        "name": "Test Tool 1",
                        "description": "Test",
                        "route": "/test",
                        "is_default": False,
                        "is_active": True
                    }
                ]
            }

            with open(export_path, 'w') as f:
                json.dump(export_data, f)

            # Create the tool (so it exists)
            test_tool = Tool(
                name="Test Tool 1",
                description="Test",
                route="/test",
                is_default=False,
                is_active=True
            )
            db.session.add(test_tool)
            db.session.commit()

            original_count = ToolAccess.query.count()

            # Import should skip ghost user
            stats = import_tool_access(
                source_path=str(export_path),
                mode='merge',
                dry_run=False
            )

            # Count should not increase (ghost user skipped)
            assert ToolAccess.query.count() == original_count
            assert len(stats['orphaned_users']) == 1
            assert stats['grants_created'] == 0

    def test_import_validates_tools_exist(self, app, init_database, tmp_path):
        """Test that import fails if tools don't exist"""
        export_path = tmp_path / "test_export.json"

        with app.app_context():
            # Create export with non-existent tool
            export_data = {
                "export_metadata": {
                    "environment": "test",
                    "timestamp": "2026-01-12T00:00:00Z",
                    "version": "1.0.0",
                    "total_users": 1,
                    "total_grants": 1,
                    "total_tools": 1
                },
                "tool_access": [
                    {
                        "username": "testuser",
                        "email": "test@example.com",
                        "tool_name": "NonExistentTool",
                        "user_id": 1
                    }
                ],
                "tools": [
                    {
                        "name": "NonExistentTool",
                        "description": "Does not exist",
                        "route": "/nonexistent",
                        "is_default": False,
                        "is_active": True
                    }
                ]
            }

            with open(export_path, 'w') as f:
                json.dump(export_data, f)

            # Import should fail with clear error
            with pytest.raises(ValueError, match="Missing tools"):
                import_tool_access(
                    source_path=str(export_path),
                    mode='merge',
                    dry_run=False
                )

    def test_import_dry_run_makes_no_changes(self, app, init_database, tmp_path):
        """Test that dry-run mode doesn't commit changes"""
        export_path = tmp_path / "test_export.json"

        with app.app_context():
            # Export current state
            export_tool_access(environment='local', output_path=str(export_path))

            # Delete all grants
            original_count = ToolAccess.query.count()
            ToolAccess.query.delete()
            db.session.commit()

            assert ToolAccess.query.count() == 0

            # Import with dry-run
            stats = import_tool_access(
                source_path=str(export_path),
                mode='merge',
                dry_run=True
            )

            # No changes should be made
            assert ToolAccess.query.count() == 0
            # But stats should show what would be created
            assert stats['grants_created'] > 0

    def test_import_idempotent_operation(self, app, init_database, tmp_path):
        """Test that importing the same data twice is safe"""
        export_path = tmp_path / "test_export.json"

        with app.app_context():
            # Export current state
            export_tool_access(environment='local', output_path=str(export_path))

            original_count = ToolAccess.query.count()

            # Import once
            stats1 = import_tool_access(
                source_path=str(export_path),
                mode='merge',
                dry_run=False
            )

            count_after_first = ToolAccess.query.count()

            # Import again (should skip all)
            stats2 = import_tool_access(
                source_path=str(export_path),
                mode='merge',
                dry_run=False
            )

            count_after_second = ToolAccess.query.count()

            # Second import should skip everything
            assert stats2['grants_created'] == 0
            assert stats2['grants_skipped'] > 0
            assert count_after_second == count_after_first


class TestExportImportRoundtrip:
    """Tests for export -> import roundtrip"""

    def test_export_import_roundtrip_preserves_data(self, app, init_database, tmp_path):
        """Test that exporting and re-importing preserves all data"""
        export_path = tmp_path / "roundtrip_export.json"

        with app.app_context():
            # Export
            export_tool_access(environment='local', output_path=str(export_path))

            # Get original counts
            original_grant_count = ToolAccess.query.count()
            original_grants = {
                (g.user_id, g.tool_name)
                for g in ToolAccess.query.all()
            }

            # Delete all grants
            ToolAccess.query.delete()
            db.session.commit()

            assert ToolAccess.query.count() == 0

            # Re-import
            import_tool_access(
                source_path=str(export_path),
                mode='merge',
                dry_run=False
            )

            # Verify count matches
            assert ToolAccess.query.count() == original_grant_count

            # Verify all grants are present
            restored_grants = {
                (g.user_id, g.tool_name)
                for g in ToolAccess.query.all()
            }

            assert original_grants == restored_grants

    def test_export_import_user_matching_by_email(self, app, init_database, tmp_path):
        """Test that import matches users by (username, email) not user_id"""
        export_path = tmp_path / "test_export.json"

        with app.app_context():
            # Export current state
            export_tool_access(environment='local', output_path=str(export_path))

            # Load export and modify user_ids (simulate different database)
            with open(export_path, 'r') as f:
                data = json.load(f)

            # Change all user_ids to 9999 (invalid)
            for grant in data['tool_access']:
                grant['user_id'] = 9999

            # Write back
            with open(export_path, 'w') as f:
                json.dump(data, f, indent=2)

            # Delete all grants
            ToolAccess.query.delete()
            db.session.commit()

            # Import should still work (matches by username/email, not user_id)
            stats = import_tool_access(
                source_path=str(export_path),
                mode='merge',
                dry_run=False
            )

            # Should have created grants (matched by username/email)
            assert stats['grants_created'] > 0
            assert ToolAccess.query.count() > 0


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_import_empty_export(self, app, init_database, tmp_path):
        """Test importing an export with no grants"""
        export_path = tmp_path / "empty_export.json"

        with app.app_context():
            export_data = {
                "export_metadata": {
                    "environment": "test",
                    "timestamp": "2026-01-12T00:00:00Z",
                    "version": "1.0.0",
                    "total_users": 0,
                    "total_grants": 0,
                    "total_tools": 0
                },
                "tool_access": [],
                "tools": []
            }

            with open(export_path, 'w') as f:
                json.dump(export_data, f)

            # Should succeed without errors
            stats = import_tool_access(
                source_path=str(export_path),
                mode='merge',
                dry_run=False
            )

            assert stats['grants_created'] == 0
            assert stats['grants_skipped'] == 0

    def test_import_nonexistent_file(self, app, init_database):
        """Test importing a file that doesn't exist"""
        with app.app_context():
            with pytest.raises(FileNotFoundError):
                import_tool_access(
                    source_path="/nonexistent/file.json",
                    mode='merge',
                    dry_run=False
                )

    def test_export_to_readonly_location_fails_gracefully(self, app, init_database):
        """Test that export fails gracefully if output path is readonly"""
        with app.app_context():
            # Try to write to a location that doesn't exist
            with pytest.raises(Exception):  # Could be FileNotFoundError or PermissionError
                export_tool_access(
                    environment='local',
                    output_path='/nonexistent/readonly/path/export.json'
                )
