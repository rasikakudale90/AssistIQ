import os
from typing import Optional
from pathlib import Path

from backend.core.errors import NotFoundException
from backend.providers.storage.base import StorageProvider


class LocalStorageProvider(StorageProvider):
    """
    Local filesystem storage provider for development and testing environments.
    Stores files under the `uploads/` root directory.
    """

    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        storage_path: str,
        file_bytes: bytes,
        content_type: str,
    ) -> str:
        target_path = self.base_dir / storage_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        return storage_path

    async def download_file(self, storage_path: str) -> bytes:
        target_path = self.base_dir / storage_path
        if not target_path.exists():
            raise NotFoundException(f"Attachment file '{storage_path}' not found on storage.")

        with open(target_path, "rb") as f:
            return f.read()

    async def get_download_url(self, storage_path: str, expires_in: int = 3600) -> str:
        # In local development, points to the backend download route
        return f"/api/v1/attachments/file/{storage_path}"

    async def delete_file(self, storage_path: str) -> bool:
        target_path = self.base_dir / storage_path
        if target_path.exists():
            target_path.unlink()
            return True
        return False
