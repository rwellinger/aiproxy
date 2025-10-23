"""Service for adding text overlays to images with perfect spelling"""

from pathlib import Path
from typing import Any

from loguru import logger
from PIL import Image, ImageDraw, ImageFont


class ImageTextOverlayService:
    """Creates text overlays on images using Pillow"""

    FONTS_DIR = Path(__file__).parent.parent.parent / "fonts"

    # Font mappings
    FONT_FILES = {
        "bold": "Montserrat-Bold.ttf",
        "elegant": "PlayfairDisplay-Regular.ttf",
        "modern": "Roboto-Black.ttf",
    }

    @staticmethod
    def add_text_overlay(
        image_path: str,
        title: str,
        artist: str | None = None,
        font_style: str = "bold",
        position: str = "top",
        text_color: str = "#FFD700",  # Gold
        outline_color: str = "#000000",  # Black
        outline_width: int = 3,
    ) -> dict[str, Any]:
        """
        Add text overlay to image with perfect spelling

        Args:
            image_path: Path to generated image
            title: Title text (will be uppercase)
            artist: Optional artist name (will be uppercase)
            font_style: Font style (bold/elegant/modern)
            position: Text position (top/center/bottom)
            text_color: Hex color for text (e.g., "#FFD700")
            outline_color: Hex color for outline (e.g., "#000000")
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

            # Calculate font size (8% of image height)
            font_size = int(img.height * 0.08)

            # Load font
            font_file = ImageTextOverlayService.FONT_FILES.get(font_style, "Montserrat-Bold.ttf")
            font_path = ImageTextOverlayService.FONTS_DIR / font_file

            if not font_path.exists():
                logger.warning(f"Font not found: {font_path}, using default")
                font = ImageFont.load_default()
            else:
                font = ImageFont.truetype(str(font_path), font_size)

            # Build text
            title_text = title.upper()
            full_text = f"{title_text}\nBY {artist.upper()}" if artist else title_text

            # Convert hex colors to RGB
            text_rgb = ImageTextOverlayService._hex_to_rgb(text_color)
            outline_rgb = ImageTextOverlayService._hex_to_rgb(outline_color)

            # Calculate text position
            bbox = draw.multiline_textbbox((0, 0), full_text, font=font, align="center")
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (img.width - text_width) // 2
            y = ImageTextOverlayService._calculate_y_position(position, img.height, text_height)

            # Draw outline (for readability)
            for adj_x in range(-outline_width, outline_width + 1):
                for adj_y in range(-outline_width, outline_width + 1):
                    if adj_x != 0 or adj_y != 0:  # Skip center
                        draw.multiline_text(
                            (x + adj_x, y + adj_y),
                            full_text,
                            font=font,
                            fill=outline_rgb,
                            align="center",
                        )

            # Draw main text
            draw.multiline_text((x, y), full_text, font=font, fill=text_rgb, align="center")

            # Save modified image
            output_path = image_path.replace(".png", "_with_text.png")
            img.convert("RGB").save(output_path)

            metadata = {
                "title": title,
                "artist": artist,
                "font_style": font_style,
                "position": position,
                "text_color": text_color,
                "outline_color": outline_color,
            }

            logger.info("Text overlay added successfully", output_path=output_path)
            return {"output_path": output_path, "metadata": metadata}

        except Exception as e:
            logger.error("Text overlay failed", error=str(e), image_path=image_path)
            raise

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def _calculate_y_position(position: str, img_height: int, text_height: int) -> int:
        """Calculate Y position based on preference"""
        if position == "top":
            return int(img_height * 0.1)  # 10% from top
        elif position == "center":
            return (img_height - text_height) // 2
        else:  # bottom
            return int(img_height * 0.80)  # 20% from bottom
