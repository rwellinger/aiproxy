"""Unit tests for ImageTextOverlayServiceV2 (without infrastructure dependencies)"""

from business.image_text_overlay_service_v2 import ImageTextOverlayServiceV2


class TestImageTextOverlayServiceV2:
    """Test ImageTextOverlayServiceV2 static methods and logic"""

    def test_hex_to_rgb_with_hash(self):
        """Test hex color conversion with hash prefix"""
        assert ImageTextOverlayServiceV2._hex_to_rgb("#FFD700") == (255, 215, 0)
        assert ImageTextOverlayServiceV2._hex_to_rgb("#000000") == (0, 0, 0)
        assert ImageTextOverlayServiceV2._hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_hex_to_rgb_without_hash(self):
        """Test hex color conversion without hash prefix"""
        assert ImageTextOverlayServiceV2._hex_to_rgb("FFD700") == (255, 215, 0)
        assert ImageTextOverlayServiceV2._hex_to_rgb("000000") == (0, 0, 0)
        assert ImageTextOverlayServiceV2._hex_to_rgb("FFFFFF") == (255, 255, 255)

    def test_hex_to_rgb_lowercase(self):
        """Test hex color conversion handles lowercase"""
        assert ImageTextOverlayServiceV2._hex_to_rgb("#ff5733") == (255, 87, 51)
        assert ImageTextOverlayServiceV2._hex_to_rgb("ff5733") == (255, 87, 51)

    def test_font_files_mapping(self):
        """Test font style mappings are complete"""
        assert "bold" in ImageTextOverlayServiceV2.FONT_FILES
        assert "elegant" in ImageTextOverlayServiceV2.FONT_FILES
        assert "light" in ImageTextOverlayServiceV2.FONT_FILES

        # Verify file names
        assert ImageTextOverlayServiceV2.FONT_FILES["bold"] == "Anton-Regular.ttf"
        assert ImageTextOverlayServiceV2.FONT_FILES["elegant"] == "PlayfairDisplay-Regular.ttf"
        assert ImageTextOverlayServiceV2.FONT_FILES["light"] == "Roboto-Light.ttf"

    def test_grid_positions_all_defined(self):
        """Test all 9 grid positions are defined"""
        expected_positions = [
            "top-left",
            "top-center",
            "top-right",
            "middle-left",
            "center",
            "middle-right",
            "bottom-left",
            "bottom-center",
            "bottom-right",
        ]
        for pos in expected_positions:
            assert pos in ImageTextOverlayServiceV2.GRID_POSITIONS

    def test_grid_positions_coordinates(self):
        """Test grid position coordinate values"""
        # Corner positions
        assert ImageTextOverlayServiceV2.GRID_POSITIONS["top-left"] == (0.10, 0.10)
        assert ImageTextOverlayServiceV2.GRID_POSITIONS["top-right"] == (0.90, 0.10)
        assert ImageTextOverlayServiceV2.GRID_POSITIONS["bottom-left"] == (0.10, 0.90)
        assert ImageTextOverlayServiceV2.GRID_POSITIONS["bottom-right"] == (0.90, 0.90)

        # Center positions
        assert ImageTextOverlayServiceV2.GRID_POSITIONS["center"] == (0.50, 0.50)
        assert ImageTextOverlayServiceV2.GRID_POSITIONS["top-center"] == (0.50, 0.10)
        assert ImageTextOverlayServiceV2.GRID_POSITIONS["bottom-center"] == (0.50, 0.90)

        # Middle positions
        assert ImageTextOverlayServiceV2.GRID_POSITIONS["middle-left"] == (0.10, 0.50)
        assert ImageTextOverlayServiceV2.GRID_POSITIONS["middle-right"] == (0.90, 0.50)

    def test_grid_positions_valid_ranges(self):
        """Test all grid positions are within valid range (0.0 - 1.0)"""
        for pos_name, (x, y) in ImageTextOverlayServiceV2.GRID_POSITIONS.items():
            assert 0.0 <= x <= 1.0, f"{pos_name} x coordinate {x} out of range"
            assert 0.0 <= y <= 1.0, f"{pos_name} y coordinate {y} out of range"
