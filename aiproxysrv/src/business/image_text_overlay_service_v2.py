"""Service for adding text overlays to images with perfect spelling - Version 2"""

import time
from pathlib import Path
from typing import Any

from loguru import logger
from PIL import Image, ImageDraw, ImageFont


class ImageTextOverlayServiceV2:
    """Creates text overlays on images using Pillow with advanced positioning"""

    FONTS_DIR = Path(__file__).parent.parent.parent / "fonts"

    # Font mappings
    FONT_FILES = {
        "bold": "Anton-Regular.ttf",  # Heavy display font
        "elegant": "PlayfairDisplay-Regular.ttf",  # Serif
        "light": "Roboto-Light.ttf",  # Thin sans-serif
    }

    # Grid position mappings (3x3 grid)
    GRID_POSITIONS = {
        "top-left": (0.10, 0.10),  # 10% from left, 10% from top
        "top-center": (0.50, 0.10),  # centered horizontally, 10% from top
        "top-right": (0.90, 0.10),  # 90% from left (10% from right), 10% from top
        "middle-left": (0.10, 0.50),  # 10% from left, centered vertically
        "center": (0.50, 0.50),  # centered both ways
        "middle-right": (0.90, 0.50),  # 90% from left, centered vertically
        "bottom-left": (0.10, 0.90),  # 10% from left, 90% from top (10% from bottom)
        "bottom-center": (0.50, 0.90),  # centered horizontally, 90% from top
        "bottom-right": (0.90, 0.90),  # 90% from left, 90% from top
    }

    @staticmethod
    def add_text_overlay(
        image_path: str,
        title: str,
        artist: str | None = None,
        font_style: str = "bold",
        # Title specific
        title_position: str | dict[str, float] = "center",  # Grid string or {"x": 0.5, "y": 0.3}
        title_font_size: float | int = 80,  # Pixels (40-200) or Percentage (0.05-0.15)
        title_color: str = "#FFFFFF",
        title_outline_color: str = "#000000",
        # Artist specific
        artist_position: str | dict[str, float] | None = None,  # Grid, custom dict, or None
        artist_font_size: float | int = 40,  # Pixels (30-100) or Percentage (0.03-0.15)
        artist_color: str | None = None,
        artist_outline_color: str | None = None,
        artist_font_style: str | None = None,  # If None, uses same as title
        # Common
        outline_width: int = 3,
    ) -> dict[str, Any]:
        """
        Add text overlay to image with perfect spelling (V2 - Advanced)

        Args:
            image_path: Path to generated image
            title: Title text (will be uppercase)
            artist: Optional artist name (will be uppercase with "BY" prefix)
            font_style: Font style for title (bold/elegant/light)
            title_position: Grid position (e.g., "center") or custom dict ({"x": 0.5, "y": 0.3})
            title_font_size: Font size in pixels (40-200) or as percentage (0.05-0.15, legacy)
            title_color: Hex color for title text
            title_outline_color: Hex outline color for title
            artist_position: Grid position, custom dict, or None (below title)
            artist_font_size: Font size in pixels (30-100) or as percentage (0.03-0.15, legacy)
            artist_color: Hex color for artist (if None, uses title_color)
            artist_outline_color: Hex outline color for artist (if None, uses title_outline_color)
            artist_font_style: Font style for artist (if None, uses same as title)
            outline_width: Pixel width of outline

        Returns:
            {
                "output_path": "/path/to/image_with_text.png",
                "metadata": {...}
            }
        """
        try:
            # Load image
            img = Image.open(image_path).convert("RGBA")
            draw = ImageDraw.Draw(img)

            # Load title font
            title_font_file = ImageTextOverlayServiceV2.FONT_FILES.get(font_style, "Anton-Regular.ttf")
            title_font_path = ImageTextOverlayServiceV2.FONTS_DIR / title_font_file

            if not title_font_path.exists():
                logger.warning(f"Title font not found: {title_font_path}, using default")
                title_font_path = None

            # Draw title
            ImageTextOverlayServiceV2._draw_text(
                draw=draw,
                img_size=(img.width, img.height),
                text=title.upper(),
                position=title_position,
                font_size_pct=title_font_size,
                text_color=title_color,
                outline_color=title_outline_color,
                outline_width=outline_width,
                font_path=title_font_path,
            )

            # Draw artist if provided
            if artist:
                artist_text = f"BY {artist.upper()}"
                actual_artist_pos = artist_position if artist_position else title_position
                actual_artist_color = artist_color if artist_color else title_color
                actual_artist_outline = artist_outline_color if artist_outline_color else title_outline_color

                # Artist font: use artist_font_style if provided, else same as title
                actual_artist_font_style = artist_font_style if artist_font_style else font_style
                artist_font_file = ImageTextOverlayServiceV2.FONT_FILES.get(
                    actual_artist_font_style, "Anton-Regular.ttf"
                )
                artist_font_path = ImageTextOverlayServiceV2.FONTS_DIR / artist_font_file

                if not artist_font_path.exists():
                    logger.warning(f"Artist font not found: {artist_font_path}, using default")
                    artist_font_path = None

                ImageTextOverlayServiceV2._draw_text(
                    draw=draw,
                    img_size=(img.width, img.height),
                    text=artist_text,
                    position=actual_artist_pos,
                    font_size_pct=artist_font_size,
                    text_color=actual_artist_color,
                    outline_color=actual_artist_outline,
                    outline_width=outline_width,
                    font_path=artist_font_path,
                    offset_y=int(img.height * title_font_size * 1.2) if not artist_position else 0,
                )

            # Save modified image with timestamp to ensure unique filename
            # Extract file extension and base path
            image_pathobj = Path(image_path)
            base_name = image_pathobj.stem  # filename without extension
            extension = image_pathobj.suffix  # e.g., ".png"
            parent_dir = image_pathobj.parent

            timestamp = int(time.time())
            output_filename = f"{base_name}_with_text_{timestamp}{extension}"
            output_path = str(parent_dir / output_filename)

            img.convert("RGB").save(output_path)

            metadata = {
                "title": title,
                "artist": artist,
                "font_style": font_style,
                "title_position": title_position,
                "title_font_size": title_font_size,
                "title_color": title_color,
                "artist_position": artist_position,
                "artist_font_size": artist_font_size,
                "artist_color": artist_color,
                "artist_font_style": artist_font_style,
            }

            logger.info("Text overlay added successfully (V2)", output_path=output_path)
            return {"output_path": output_path, "metadata": metadata}

        except Exception as e:
            logger.error("Text overlay failed (V2)", error=str(e), image_path=image_path)
            raise

    @staticmethod
    def _draw_text(
        draw: ImageDraw.ImageDraw,
        img_size: tuple[int, int],
        text: str,
        position: str | dict[str, float],
        font_size_pct: float | int,
        text_color: str,
        outline_color: str,
        outline_width: int,
        font_path: Path | None,
        offset_y: int = 0,
    ) -> None:
        """Draw single text element on image"""
        img_width, img_height = img_size

        # Calculate font size (accept both pixels and percentage)
        if isinstance(font_size_pct, int) or (isinstance(font_size_pct, float) and font_size_pct >= 1.0):
            # Pixel value (>= 1.0)
            font_size = int(font_size_pct)
        else:
            # Percentage value (< 1.0) - legacy support
            font_size = int(img_height * font_size_pct)

        # Load font
        font = ImageFont.truetype(str(font_path), font_size) if font_path else ImageFont.load_default()

        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Get left padding from bounding box (bbox[0] is the left offset)
        bbox_left_offset = bbox[0]

        # Calculate position (support both grid and custom)
        is_custom_position = isinstance(position, dict)

        if is_custom_position:
            # Custom position (x, y as 0.0-1.0)
            grid_x_pct = max(0.0, min(1.0, position.get("x", 0.5)))
            grid_y_pct = max(0.0, min(1.0, position.get("y", 0.5)))
        else:
            # Grid position (string like "center", "top-left", etc.)
            grid_x_pct, grid_y_pct = ImageTextOverlayServiceV2.GRID_POSITIONS.get(position, (0.5, 0.5))

        # Calculate pixel coordinates
        if is_custom_position:
            # CUSTOM POSITION: Use 'lt' anchor but compensate for left padding
            # This matches the frontend marker position (top-left of first visible character)
            x = int(img_width * grid_x_pct) - bbox_left_offset  # Remove left padding from bounding box
            y = int(img_height * grid_y_pct)  # Top edge at click point
        else:
            # GRID POSITION: Use alignment based on grid position
            if grid_x_pct == 0.10:  # Left-aligned
                x = int(img_width * grid_x_pct)
            elif grid_x_pct == 0.90:  # Right-aligned
                x = int(img_width * grid_x_pct) - text_width
            else:  # Center-aligned
                x = int(img_width * grid_x_pct) - (text_width // 2)

            if grid_y_pct == 0.10:  # Top-aligned
                y = int(img_height * grid_y_pct)
            elif grid_y_pct == 0.90:  # Bottom-aligned
                y = int(img_height * grid_y_pct) - text_height
            else:  # Center-aligned
                y = int(img_height * grid_y_pct) - (text_height // 2)

        # Apply offset (for artist below title)
        y += offset_y

        # Convert colors
        text_rgb = ImageTextOverlayServiceV2._hex_to_rgb(text_color)
        outline_rgb = ImageTextOverlayServiceV2._hex_to_rgb(outline_color)

        # For custom positions: use 'lt' anchor (left-top of bounding box, matches Canvas top baseline)
        # For grid positions: use default anchor (left-baseline)
        anchor = "lt" if is_custom_position else None

        # Draw outline
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                if adj_x != 0 or adj_y != 0:  # Skip center
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_rgb, anchor=anchor)

        # Draw main text
        draw.text((x, y), text, font=font, fill=text_rgb, anchor=anchor)

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
