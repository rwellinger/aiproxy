"""
S3 Proxy Service - Generic service for serving S3 resources via backend proxy.

CRITICAL Architecture Rule:
- Frontend MUST NEVER receive presigned URLs (MinIO, AWS, etc.)
- ALL S3 resources MUST be served via backend proxy routes
- This service provides generic resource streaming from S3 to browser

Usage:
    from adapters.s3.s3_proxy_service import s3_proxy_service

    # In Flask route:
    return s3_proxy_service.serve_resource(
        bucket="my-bucket",
        s3_key="path/to/file.jpg",
        filename="file.jpg"
    )
"""

import traceback
from io import BytesIO

from flask import Response, send_file

from infrastructure.storage import get_storage
from utils.logger import logger


class S3ProxyService:
    """Generic service for proxying S3 resources to browser via backend"""

    @staticmethod
    def serve_resource(bucket: str, s3_key: str, filename: str) -> Response:
        """
        Stream S3 resource to browser (generic proxy method)

        Args:
            bucket: S3 bucket name
            s3_key: S3 object key (full path)
            filename: Original filename (for Content-Type detection)

        Returns:
            Flask Response with binary data

        Raises:
            Exception: If S3 download fails

        Example:
            >>> s3_proxy_service.serve_resource(
            ...     bucket="images",
            ...     s3_key="shared/abc-123.png",
            ...     filename="my-image.png"
            ... )
        """
        try:
            # Download from S3
            storage = get_storage(bucket=bucket)
            data = storage.download(s3_key)

            # Determine Content-Type from filename
            content_type = S3ProxyService._get_content_type(filename)

            logger.debug("Streaming S3 resource", bucket=bucket, s3_key=s3_key, content_type=content_type)

            return send_file(BytesIO(data), mimetype=content_type, as_attachment=False, download_name=filename)

        except Exception as e:
            logger.error(
                "Error serving S3 resource",
                bucket=bucket,
                s3_key=s3_key,
                error=str(e),
                error_type=type(e).__name__,
                stacktrace=traceback.format_exc(),
            )
            raise

    @staticmethod
    def _get_content_type(filename: str) -> str:
        """
        Determine Content-Type from filename extension

        Args:
            filename: Original filename

        Returns:
            MIME type string

        Examples:
            >>> S3ProxyService._get_content_type("image.png")
            'image/png'
            >>> S3ProxyService._get_content_type("photo.jpg")
            'image/jpeg'
            >>> S3ProxyService._get_content_type("cover.webp")
            'image/webp'
            >>> S3ProxyService._get_content_type("unknown.xyz")
            'application/octet-stream'
        """
        extension = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

        # Image types
        if extension in ["jpg", "jpeg"]:
            return "image/jpeg"
        elif extension == "png":
            return "image/png"
        elif extension == "webp":
            return "image/webp"
        elif extension == "gif":
            return "image/gif"
        elif extension == "svg":
            return "image/svg+xml"

        # Audio types (for future song releases)
        elif extension == "mp3":
            return "audio/mpeg"
        elif extension == "wav":
            return "audio/wav"
        elif extension == "flac":
            return "audio/flac"
        elif extension == "ogg":
            return "audio/ogg"

        # Document types (for future features)
        elif extension == "pdf":
            return "application/pdf"
        elif extension == "json":
            return "application/json"
        elif extension == "txt":
            return "text/plain"

        # Default
        else:
            return "application/octet-stream"


# Singleton instance
s3_proxy_service = S3ProxyService()
