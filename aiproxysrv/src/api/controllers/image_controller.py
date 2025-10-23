"""Image Controller - Handles HTTP requests for image operations"""

import logging
from pathlib import Path
from typing import Any

from business.image_business_service import ImageBusinessService, ImageGenerationError
from business.image_text_overlay_service import ImageTextOverlayService


logger = logging.getLogger(__name__)


class ImageController:
    """Controller for image HTTP request handling"""

    def __init__(self):
        self.business_service = ImageBusinessService()

    def generate_image(
        self,
        prompt: str,
        size: str,
        title: str | None = None,
        user_prompt: str | None = None,
        artistic_style: str | None = None,
        composition: str | None = None,
        lighting: str | None = None,
        color_palette: str | None = None,
        detail_level: str | None = None,
    ) -> tuple[dict[str, Any], int]:
        """
        Generate image via business service

        Args:
            prompt: AI-enhanced image generation prompt (from Ollama)
            size: Image size specification
            title: Optional image title
            user_prompt: Optional original user input (before AI enhancement)
            artistic_style: Optional artistic style (auto, photorealistic, digital-art, etc.)
            composition: Optional composition (auto, portrait, landscape, etc.)
            lighting: Optional lighting (auto, natural, studio, dramatic, etc.)
            color_palette: Optional color palette (auto, vibrant, muted, etc.)
            detail_level: Optional detail level (auto, minimal, moderate, highly-detailed)

        Returns:
            Tuple of (response_data, status_code)
        """
        # Basic validation
        if not prompt or not size:
            return {"error": "Missing prompt or size"}, 400

        try:
            result = self.business_service.generate_image(
                prompt=prompt,
                size=size,
                title=title,
                user_prompt=user_prompt,
                artistic_style=artistic_style,
                composition=composition,
                lighting=lighting,
                color_palette=color_palette,
                detail_level=detail_level,
            )
            return result, 200

        except ImageGenerationError as e:
            logger.error(f"Image generation failed: {e}")
            return {"error": str(e)}, 500
        except Exception as e:
            logger.error(f"Unexpected error in image generation: {type(e).__name__}: {e}")
            return {"error": "Internal server error"}, 500

    def get_images(
        self,
        limit: int = 20,
        offset: int = 0,
        search: str = "",
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ) -> tuple[dict[str, Any], int]:
        """
        Get list of generated images with pagination, search and sorting

        Args:
            limit: Number of images to return (default 20)
            offset: Number of images to skip (default 0)
            search: Search term for title and prompt (default '')
            sort_by: Field to sort by (default 'created_at')
            sort_direction: Sort direction 'asc' or 'desc' (default 'desc')

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            result = self.business_service.get_images_with_pagination(
                limit=limit, offset=offset, search=search, sort_by=sort_by, sort_direction=sort_direction
            )
            return result, 200

        except ImageGenerationError as e:
            logger.error(f"Failed to retrieve images: {e}")
            return {"error": str(e)}, 500
        except Exception as e:
            logger.error(f"Unexpected error retrieving images: {type(e).__name__}: {e}")
            return {"error": "Internal server error"}, 500

    def get_image_by_id(self, image_id: str) -> tuple[dict[str, Any], int]:
        """
        Get single image by ID

        Args:
            image_id: ID of the image

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            result = self.business_service.get_image_details(image_id)

            if result is None:
                return {"error": "Image not found"}, 404

            return result, 200

        except ImageGenerationError as e:
            logger.error(f"Failed to retrieve image {image_id}: {e}")
            return {"error": str(e)}, 500
        except Exception as e:
            logger.error(f"Unexpected error retrieving image {image_id}: {type(e).__name__}: {e}")
            return {"error": "Internal server error"}, 500

    def delete_image(self, image_id: str) -> tuple[dict[str, Any], int]:
        """
        Delete image by ID

        Args:
            image_id: ID of the image to delete

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            success = self.business_service.delete_single_image(image_id)

            if not success:
                return {"error": "Image not found"}, 404

            return {"message": "Image deleted successfully"}, 200

        except ImageGenerationError as e:
            logger.error(f"Failed to delete image {image_id}: {e}")
            return {"error": str(e)}, 500
        except Exception as e:
            logger.error(f"Unexpected error deleting image {image_id}: {type(e).__name__}: {e}")
            return {"error": "Internal server error"}, 500

    def bulk_delete_images(self, image_ids: list[str]) -> tuple[dict[str, Any], int]:
        """
        Delete multiple images by IDs

        Args:
            image_ids: List of image IDs to delete

        Returns:
            Tuple of (response_data, status_code)
        """
        if not image_ids:
            return {"error": "No image IDs provided"}, 400

        if len(image_ids) > 100:
            return {"error": "Too many images (max 100 per request)"}, 400

        try:
            result = self.business_service.bulk_delete_images(image_ids)

            # Determine response status based on results
            summary = result["summary"]
            if summary["deleted"] > 0:
                status_code = 200
                if summary["not_found"] > 0 or summary["errors"] > 0:
                    status_code = 207  # Multi-Status
            else:
                status_code = 400 if summary["errors"] > 0 else 404

            return result, status_code

        except ImageGenerationError as e:
            logger.error(f"Bulk delete failed: {e}")
            return {"error": str(e)}, 500
        except Exception as e:
            logger.error(f"Unexpected error in bulk delete: {type(e).__name__}: {e}")
            return {"error": "Internal server error"}, 500

    def update_image_metadata(self, image_id: str, title: str = None, tags: str = None) -> tuple[dict[str, Any], int]:
        """
        Update image metadata (title and/or tags)

        Args:
            image_id: ID of the image to update
            title: Optional new title
            tags: Optional tags (comma-separated string)

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            result = self.business_service.update_image_metadata(image_id, title, tags)

            if result is None:
                return {"error": "Image not found"}, 404

            return result, 200

        except ImageGenerationError as e:
            logger.error(f"Failed to update image {image_id}: {e}")
            return {"error": str(e)}, 500
        except Exception as e:
            logger.error(f"Unexpected error updating image {image_id}: {type(e).__name__}: {e}")
            return {"error": "Internal server error"}, 500

    def add_text_overlay(
        self,
        image_id: str,
        user_id: str,
        title: str,
        artist: str | None = None,
        font_style: str = "bold",
        position: str = "top",
        text_color: str = "#FFD700",
        outline_color: str = "#000000",
    ) -> tuple[dict[str, Any], int]:
        """
        Add text overlay to existing image

        Args:
            image_id: ID of the source image
            user_id: ID of the authenticated user
            title: Title text to render
            artist: Optional artist name
            font_style: Font style (bold/elegant/modern)
            position: Text position (top/center/bottom)
            text_color: Hex color for text
            outline_color: Hex color for outline

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get original image details
            original_image = self.business_service.get_image_details(image_id)

            if original_image is None:
                return {"error": "Image not found"}, 404

            # Verify ownership (user_id from JWT must match image owner)
            if str(original_image.get("user_id")) != str(user_id):
                return {"error": "Unauthorized: You don't own this image"}, 403

            # Get file path from original image
            file_path = original_image.get("file_path")
            if not file_path:
                return {"error": "Image file path not found"}, 500

            # Add text overlay using service
            result = ImageTextOverlayService.add_text_overlay(
                image_path=file_path,
                title=title,
                artist=artist,
                font_style=font_style,
                position=position,
                text_color=text_color,
                outline_color=outline_color,
            )

            # Create new image record (keep original untouched)
            from db.image_service import ImageService

            new_image = ImageService.save_generated_image(
                prompt=original_image.get("prompt", ""),
                size=original_image.get("size", "1024x1024"),
                filename=Path(result["output_path"]).name,
                file_path=result["output_path"],
                local_url=f"/api/v1/image/{Path(result['output_path']).name}",
                model_used=original_image.get("model_used", "dall-e-3"),
                prompt_hash=original_image.get("prompt_hash", ""),
                title=title,
                user_prompt=original_image.get("user_prompt", ""),
                enhanced_prompt=original_image.get("enhanced_prompt"),
                artistic_style=original_image.get("artistic_style"),
                composition=original_image.get("composition"),
                lighting=original_image.get("lighting"),
                color_palette=original_image.get("color_palette"),
                detail_level=original_image.get("detail_level"),
            )

            # Update the new image with text_overlay_metadata
            # (save_generated_image doesn't accept this parameter yet)
            if new_image:
                from db.database import SessionLocal

                db = SessionLocal()
                try:
                    new_image.text_overlay_metadata = result["metadata"]
                    db.add(new_image)
                    db.commit()
                    db.refresh(new_image)
                finally:
                    db.close()
            else:
                return {"error": "Failed to create new image record"}, 500

            logger.info(f"Text overlay created successfully for image {image_id}, new image: {new_image.id}")

            return {
                "success": True,
                "image_id": str(new_image.id),
                "image_url": new_image.local_url,
                "metadata": result["metadata"],
            }, 200

        except ImageGenerationError as e:
            logger.error(f"Text overlay failed for image {image_id}: {e}")
            return {"error": str(e)}, 500
        except Exception as e:
            logger.error(f"Unexpected error adding text overlay to image {image_id}: {type(e).__name__}: {e}")
            return {"error": f"Internal server error: {str(e)}"}, 500
