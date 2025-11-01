"""Storage Infrastructure - Factory Pattern for storage backends"""

from config.settings import STORAGE_BACKEND
from infrastructure.storage.storage_interface import StorageInterface


def get_storage(bucket: str | None = None) -> StorageInterface:
    """
    Factory function to get storage instance based on configuration

    Args:
        bucket: Optional bucket name. If None, uses default from config.

    Returns:
        StorageInterface implementation (S3Storage or FileSystemStorage)

    Raises:
        ValueError: If unknown storage backend configured
    """
    if STORAGE_BACKEND == "s3":
        from infrastructure.storage.s3_storage import S3Storage

        return S3Storage(bucket=bucket)
    elif STORAGE_BACKEND == "filesystem":
        # Fallback to filesystem storage (future implementation)
        raise NotImplementedError("Filesystem storage not yet implemented")
    else:
        raise ValueError(f"Unknown storage backend: {STORAGE_BACKEND}")


# Convenience exports
__all__ = ["get_storage", "StorageInterface"]
