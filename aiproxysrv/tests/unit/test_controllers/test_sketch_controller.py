"""Unit tests for SketchController

Note: Success cases with Pydantic model_validate() are tested via integration tests.
These unit tests focus on error handling and edge cases.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from api.controllers.sketch_controller import SketchController
from schemas.sketch_schemas import SketchCreateRequest, SketchUpdateRequest


@pytest.mark.unit
class TestSketchControllerCreate:
    """Test SketchController.create_sketch method"""

    def test_create_sketch_success(self, mock_db_session):
        """Test successful sketch creation"""
        sketch_data = SketchCreateRequest(
            title="Test Sketch",
            lyrics="[Verse 1]\nTest lyrics",
            prompt="upbeat pop",
            tags="pop, test",
        )

        # Mock the created sketch from business layer
        mock_sketch = MagicMock()
        mock_sketch.id = uuid4()
        mock_sketch.title = "Test Sketch"
        mock_sketch.lyrics = "[Verse 1]\nTest lyrics"
        mock_sketch.prompt = "upbeat pop"
        mock_sketch.tags = "pop, test"
        mock_sketch.workflow = "draft"
        mock_sketch.created_at = datetime.now()
        mock_sketch.updated_at = None

        # Mock the global sketch_service instance's create_sketch method
        with patch("db.sketch_service.sketch_service.create_sketch", return_value=mock_sketch):
            result, status_code = SketchController.create_sketch(
                sketch_data=sketch_data, db=mock_db_session
            )

            assert status_code == 201
            assert "data" in result
            assert "message" in result
            assert result["message"] == "Sketch created successfully"

    def test_create_sketch_validation_error(self, mock_db_session):
        """Test sketch creation with invalid data"""
        # Prompt is required, so missing it should raise validation error
        with pytest.raises(ValidationError):
            SketchCreateRequest(
                title="Test",
                lyrics="Test lyrics",
                # prompt is missing - should fail validation
                tags="test",
            )

    def test_create_sketch_business_layer_failure(self, mock_db_session):
        """Test sketch creation when business layer returns None"""
        sketch_data = SketchCreateRequest(
            title="Test Sketch", lyrics="Test lyrics", prompt="upbeat pop", tags="test"
        )

        # Mock the global sketch_service instance's create_sketch method returning None (failure)
        with patch("db.sketch_service.sketch_service.create_sketch", return_value=None):
            result, status_code = SketchController.create_sketch(
                sketch_data=sketch_data, db=mock_db_session
            )

            assert status_code == 500
            assert "error" in result


@pytest.mark.unit
class TestSketchControllerGetById:
    """Test SketchController.get_sketch_by_id method"""

    def test_get_sketch_by_id_not_found(self, mock_db_session):
        """Test getting non-existent sketch"""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result, status_code = SketchController.get_sketch_by_id(mock_db_session, str(uuid4()))

        assert status_code == 404
        assert "error" in result

    def test_get_sketch_by_id_invalid_uuid(self, mock_db_session):
        """Test getting sketch with invalid UUID"""
        result, status_code = SketchController.get_sketch_by_id(mock_db_session, "invalid-uuid")

        assert status_code == 400
        assert "error" in result


@pytest.mark.unit
class TestSketchControllerUpdate:
    """Test SketchController.update_sketch method"""

    def test_update_sketch_not_found(self, mock_db_session):
        """Test updating non-existent sketch"""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        update_data = SketchUpdateRequest(title="New Title")

        result, status_code = SketchController.update_sketch(
            db=mock_db_session, sketch_id=str(uuid4()), update_data=update_data
        )

        assert status_code == 404
        assert "error" in result

    def test_update_sketch_invalid_uuid(self, mock_db_session):
        """Test updating sketch with invalid UUID"""
        update_data = SketchUpdateRequest(title="New Title")

        result, status_code = SketchController.update_sketch(
            db=mock_db_session, sketch_id="invalid-uuid", update_data=update_data
        )

        assert status_code == 400
        assert "error" in result


@pytest.mark.unit
class TestSketchControllerDelete:
    """Test SketchController.delete_sketch method"""

    def test_delete_sketch_success(self, mock_db_session):
        """Test successful sketch deletion"""
        mock_sketch = MagicMock()
        mock_sketch.id = uuid4()

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_sketch

        result, status_code = SketchController.delete_sketch(mock_db_session, str(mock_sketch.id))

        assert status_code == 200
        assert "message" in result
        mock_db_session.delete.assert_called_once_with(mock_sketch)
        mock_db_session.commit.assert_called_once()

    def test_delete_sketch_not_found(self, mock_db_session):
        """Test deleting non-existent sketch"""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result, status_code = SketchController.delete_sketch(mock_db_session, str(uuid4()))

        assert status_code == 404
        assert "error" in result

    def test_delete_sketch_invalid_uuid(self, mock_db_session):
        """Test deleting sketch with invalid UUID"""
        result, status_code = SketchController.delete_sketch(mock_db_session, "invalid-uuid")

        assert status_code == 400
        assert "error" in result
