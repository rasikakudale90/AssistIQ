from abc import ABC, abstractmethod
from typing import Optional


class StorageProvider(ABC):
    """Abstract interface for file attachment storage (SRS §3.1, §7.5, §11)."""

    @abstractmethod
    async def upload_file(
        self,
        storage_path: str,
        file_bytes: bytes,
        content_type: str,
    ) -> str:
        """
        Uploads file bytes to the target path.
        Returns the persistent storage identifier or path.
        """
        pass

    @abstractmethod
    async def download_file(self, storage_path: str) -> bytes:
        """Retrieves raw file bytes from storage."""
        pass

    @abstractmethod
    async def get_download_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Generates a secure download URL or endpoint path for the file."""
        pass

    @abstractmethod
    async def delete_file(self, storage_path: str) -> bool:
        """Deletes file from storage."""
        pass
