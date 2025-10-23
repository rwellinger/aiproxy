"""Unit tests for ImageTextOverlayService"""

from business.image_text_overlay_service import ImageTextOverlayService


class TestImageTextOverlayService:
    """Test ImageTextOverlayService static methods"""

    def test_hex_to_rgb_with_hash(self):
        """Test hex color conversion with hash prefix"""
        assert ImageTextOverlayService._hex_to_rgb("#FFD700") == (255, 215, 0)
        assert ImageTextOverlayService._hex_to_rgb("#000000") == (0, 0, 0)
        assert ImageTextOverlayService._hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_hex_to_rgb_without_hash(self):
        """Test hex color conversion without hash prefix"""
        assert ImageTextOverlayService._hex_to_rgb("FFD700") == (255, 215, 0)
        assert ImageTextOverlayService._hex_to_rgb("000000") == (0, 0, 0)
        assert ImageTextOverlayService._hex_to_rgb("FFFFFF") == (255, 255, 255)

    def test_calculate_y_position_top(self):
        """Test Y position calculation for top placement"""
        y = ImageTextOverlayService._calculate_y_position("top", 1000, 100)
        assert y == 100  # 10% from top

    def test_calculate_y_position_center(self):
        """Test Y position calculation for center placement"""
        y = ImageTextOverlayService._calculate_y_position("center", 1000, 100)
        assert y == 450  # (1000 - 100) // 2

    def test_calculate_y_position_bottom(self):
        """Test Y position calculation for bottom placement"""
        y = ImageTextOverlayService._calculate_y_position("bottom", 1000, 100)
        assert y == 800  # 80% from top (20% from bottom)

    def test_calculate_y_position_default(self):
        """Test Y position calculation with unknown position (defaults to bottom)"""
        y = ImageTextOverlayService._calculate_y_position("unknown", 1000, 100)
        assert y == 800  # Same as bottom
