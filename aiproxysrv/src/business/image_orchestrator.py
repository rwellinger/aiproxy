"""Image Orchestrator - Coordinates image operations (no testable business logic)"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from business.bulk_delete_transformer import BulkDeleteTransformer, DeleteResult
from business.image_transformer import ImageTransformer
from business.image_validator import ImageValidator
from config.settings import DELETE_PHYSICAL_FILES, IMAGE_BASE_URL, IMAGES_DIR, OPENAI_MODEL
from db.image_service import ImageService
from utils.logger import logger


if TYPE_CHECKING:
    from db.models import GeneratedImage
from .file_management_service import FileManagementService


class ImageGenerationError(Exception):
    """Base exception for image generation errors"""

    pass


class ImageOrchestrator:
    """Orchestrates image operations (calls services + repository)"""

    def __init__(self):
        self.images_dir = Path(IMAGES_DIR)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.file_service = FileManagementService()

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
    ) -> dict[str, Any]:
        """
        Generate image with validation and business logic

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
            Dict containing image URL and metadata

        Raises:
            ImageGenerationError: If generation fails
        """
        # Business logic: Validate request (delegated to validator)
        from business.image_validator import ImageValidationError

        try:
            ImageValidator.validate_prompt(prompt)
            ImageValidator.validate_size(size)
        except ImageValidationError as e:
            raise ImageGenerationError(str(e)) from e

        prompt_preview = prompt[:50] + ("..." if len(prompt) > 50 else "")
        logger.info("Starting image generation", prompt_preview=prompt_preview, size=size)

        # Construct enhanced prompt with style preferences
        from .image_enhancement_service import ImageEnhancementService

        enhanced_prompt = ImageEnhancementService.construct_enhanced_prompt(
            base_prompt=prompt,
            artistic_style=artistic_style,
            composition=composition,
            lighting=lighting,
            color_palette=color_palette,
            detail_level=detail_level,
        )

        # Use enhanced_prompt for generation, or original if no styles applied
        final_prompt = enhanced_prompt if enhanced_prompt != prompt else prompt

        try:
            # Generate image via external API (delegated to external service)
            from .external_api_service import OpenAIService

            openai_service = OpenAIService()
            image_url = openai_service.generate_image(final_prompt, size)

            # Download and save image
            filename, file_path = self._process_and_save_image(image_url, prompt)

            # Build local URL
            local_url = f"{IMAGE_BASE_URL}/{filename}"

            # Save metadata to database and get the generated image record
            generated_image = self._save_image_metadata(
                user_prompt=user_prompt,
                prompt=prompt,  # Ollama-enhanced prompt
                enhanced_prompt=enhanced_prompt if enhanced_prompt != prompt else None,
                size=size,
                filename=filename,
                file_path=file_path,
                local_url=local_url,
                title=title,
                artistic_style=artistic_style,
                composition=composition,
                lighting=lighting,
                color_palette=color_palette,
                detail_level=detail_level,
            )

            logger.info(f"Image generated successfully: {filename}")
            response = {"url": local_url, "saved_path": str(file_path)}

            # Include image metadata if database save was successful
            if generated_image:
                response["id"] = str(generated_image.id)
                response["user_prompt"] = generated_image.user_prompt
                response["prompt"] = generated_image.prompt
                response["enhanced_prompt"] = generated_image.enhanced_prompt
                response["artistic_style"] = generated_image.artistic_style
                response["composition"] = generated_image.composition
                response["lighting"] = generated_image.lighting
                response["color_palette"] = generated_image.color_palette
                response["detail_level"] = generated_image.detail_level
                logger.info("Image saved to database", image_id=generated_image.id, filename=filename)
            else:
                logger.warning("Image generated but failed to save metadata to database", filename=filename)

            return response

        except Exception as e:
            logger.error("Image generation failed", error_type=type(e).__name__, error=str(e))
            raise ImageGenerationError(f"Generation failed: {e}") from e

    def get_images_with_pagination(
        self,
        limit: int = 20,
        offset: int = 0,
        search: str = "",
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ) -> dict[str, Any]:
        """
        Get paginated list of images with search and sorting

        Args:
            limit: Number of images to return
            offset: Number of images to skip
            search: Search term for filtering
            sort_by: Field to sort by
            sort_direction: Sort direction ('asc' or 'desc')

        Returns:
            Dict containing images and pagination info
        """
        try:
            images = ImageService.get_images_paginated(
                limit=limit, offset=offset, search=search, sort_by=sort_by, sort_direction=sort_direction
            )
            total_count = ImageService.get_total_images_count(search=search)

            # Transform to API response format
            image_list = [self._transform_image_to_api_format(image) for image in images]

            return {
                "images": image_list,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count,
                },
            }

        except Exception as e:
            logger.error("Error retrieving images", error=str(e))
            raise ImageGenerationError(f"Failed to retrieve images: {e}") from e

    def get_images_for_text_overlay(self) -> dict[str, Any]:
        """
        Get list of images suitable for text overlay
        - Only images with title (not NULL and not empty)
        - Sorted: composition='album-cover' first, then by created_at DESC
        - No pagination (return all matching images)

        Returns:
            Dict containing filtered and sorted images
        """
        try:
            images = ImageService.get_images_for_text_overlay()

            # Transform to API response format
            image_list = [self._transform_image_to_api_format(image) for image in images]

            return {"images": image_list}

        except Exception as e:
            logger.error("Error retrieving images for text overlay", error=str(e))
            raise ImageGenerationError(f"Failed to retrieve images for text overlay: {e}") from e

    def get_image_details(self, image_id: str) -> dict[str, Any] | None:
        """
        Get detailed information for a single image

        Args:
            image_id: ID of the image

        Returns:
            Dict containing image details or None if not found
        """
        try:
            image = ImageService.get_image_by_id(image_id)
            if not image:
                return None

            return self._transform_image_to_api_format(image, include_file_path=True)

        except Exception as e:
            logger.error("Error retrieving image", image_id=image_id, error=str(e))
            raise ImageGenerationError(f"Failed to retrieve image: {e}") from e

    def delete_single_image(self, image_id: str) -> bool:
        """
        Delete a single image including files and metadata

        Args:
            image_id: ID of the image to delete

        Returns:
            True if successful, False if image not found

        Raises:
            ImageGenerationError: If deletion fails
        """
        try:
            image = ImageService.get_image_by_id(image_id)
            if not image:
                return False

            # Delete physical file if enabled
            if DELETE_PHYSICAL_FILES:
                self.file_service.delete_file_if_exists(image.file_path)
            else:
                logger.info("Skipping physical file deletion (disabled)", file_path=image.file_path)

            # Delete metadata from database
            success = ImageService.delete_image_metadata(image_id)
            if success:
                logger.info("Image deleted successfully", image_id=image_id)
                return True
            else:
                raise ImageGenerationError("Failed to delete image metadata")

        except Exception as e:
            logger.error("Error deleting image", image_id=image_id, error_type=type(e).__name__, error=str(e))
            raise ImageGenerationError(f"Failed to delete image: {e}") from e

    def bulk_delete_images(self, image_ids: list[str]) -> dict[str, Any]:
        """
        Delete multiple images with detailed results

        Args:
            image_ids: List of image IDs to delete

        Returns:
            Dict containing deletion results and summary
        """
        # Business logic: Validate bulk delete request (delegated to validator)
        from business.image_validator import ImageValidationError

        try:
            ImageValidator.validate_bulk_delete_count(image_ids)
        except ImageValidationError as e:
            raise ImageGenerationError(str(e)) from e

        # Orchestration: Process each delete operation
        delete_results = []
        for image_id in image_ids:
            try:
                # Check if image exists
                image = ImageService.get_image_by_id(image_id)
                if not image:
                    delete_results.append(DeleteResult(image_id, "not_found"))
                    continue

                # Delete physical file if enabled
                if DELETE_PHYSICAL_FILES:
                    self.file_service.delete_file_if_exists(image.file_path)

                # Delete metadata from database
                success = ImageService.delete_image_metadata(image_id)
                if success:
                    delete_results.append(DeleteResult(image_id, "deleted"))
                    logger.info("Bulk delete: Image deleted", image_id=image_id)
                else:
                    delete_results.append(DeleteResult(image_id, "error", "Failed to delete metadata"))

            except Exception as e:
                error_msg = f"{type(e).__name__}: {e}"
                delete_results.append(DeleteResult(image_id, "error", error_msg))
                logger.error("Bulk delete: Error deleting image", image_id=image_id, error=error_msg)

        # Business logic: Aggregate results (delegated to transformer)
        aggregated_results = BulkDeleteTransformer.aggregate_results(delete_results)
        response = BulkDeleteTransformer.format_bulk_delete_response(aggregated_results, len(image_ids))

        logger.info("Bulk delete completed", summary=response["summary"])
        return response

    def update_image_metadata(self, image_id: str, title: str = None, tags: str = None) -> dict[str, Any] | None:
        """
        Update image metadata

        Args:
            image_id: ID of the image to update
            title: Optional new title
            tags: Optional tags (comma-separated string)

        Returns:
            Updated image data or None if not found
        """
        try:
            # Check if image exists
            image = ImageService.get_image_by_id(image_id)
            if not image:
                return None

            # Update metadata
            success = ImageService.update_image_metadata(image_id, title, tags)
            if not success:
                raise ImageGenerationError("Failed to update image metadata")

            logger.info("Image metadata updated successfully", image_id=image_id)

            # Return updated image data
            updated_image = ImageService.get_image_by_id(image_id)
            return self._transform_image_to_api_format(updated_image, include_file_path=True) if updated_image else None

        except Exception as e:
            logger.error("Error updating image", image_id=image_id, error_type=type(e).__name__, error=str(e))
            raise ImageGenerationError(f"Failed to update image: {e}") from e

    def _process_and_save_image(self, image_url: str, prompt: str) -> tuple[str, Path]:
        """Download and save image to filesystem"""
        # Business logic: Generate filename (delegated to transformer)
        filename = ImageTransformer.generate_filename(prompt)
        file_path = self.images_dir / filename

        # Download and save
        self.file_service.download_and_save_file(image_url, file_path)

        logger.info("Image stored", file_path=str(file_path), filename=filename)
        return filename, file_path

    def _save_image_metadata(
        self,
        prompt: str,
        size: str,
        filename: str,
        file_path: Path,
        local_url: str,
        title: str | None = None,
        user_prompt: str | None = None,
        enhanced_prompt: str | None = None,
        artistic_style: str | None = None,
        composition: str | None = None,
        lighting: str | None = None,
        color_palette: str | None = None,
        detail_level: str | None = None,
    ) -> Optional["GeneratedImage"]:
        """Save image metadata to database"""
        # Business logic: Generate prompt hash (delegated to transformer)
        prompt_hash = ImageTransformer.generate_prompt_hash(prompt)

        return ImageService.save_generated_image(
            user_prompt=user_prompt,
            prompt=prompt,
            enhanced_prompt=enhanced_prompt,
            size=size,
            filename=filename,
            file_path=str(file_path),
            local_url=local_url,
            model_used=OPENAI_MODEL,
            prompt_hash=prompt_hash,
            title=title,
            artistic_style=artistic_style,
            composition=composition,
            lighting=lighting,
            color_palette=color_palette,
            detail_level=detail_level,
        )

    def _transform_image_to_api_format(self, image, include_file_path: bool = False) -> dict[str, Any]:
        """Transform database image object to API response format"""
        # Business logic: Transform to API format (delegated to transformer)
        return ImageTransformer.transform_image_to_api_format(image, include_file_path)
