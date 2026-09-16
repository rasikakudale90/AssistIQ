import logging
from typing import Optional
import httpx

from backend.core.config import settings
from backend.core.errors import ValidationException, NotFoundException
from backend.providers.storage.base import StorageProvider

logger = logging.getLogger("assistiq.storage.supabase")


class SupabaseStorageProvider(StorageProvider):
    """
    Supabase Storage provider for staging and production (SRS §3.1, §7.5).
    Interacts with Supabase Storage REST API over HTTPS.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        service_role_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
    ):
        self.supabase_url = (supabase_url or settings.SUPABASE_URL or "").rstrip("/")
        self.service_role_key = service_role_key or settings.SUPABASE_SERVICE_ROLE_KEY
        self.bucket_name = bucket_name or settings.SUPABASE_BUCKET_NAME

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": self.service_role_key or "",
        }

    async def upload_file(
        self,
        storage_path: str,
        file_bytes: bytes,
        content_type: str,
    ) -> str:
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{storage_path}"
        headers = self._headers()
        headers["Content-Type"] = content_type

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, content=file_bytes)
            if resp.status_code not in [200, 201]:
                logger.error(f"Supabase Storage upload error ({resp.status_code}): {resp.text}")
                raise ValidationException(f"Failed to upload attachment to Supabase Storage: {resp.text}")

        return storage_path

    async def download_file(self, storage_path: str) -> bytes:
        url = f"{self.supabase_url}/storage/v1/object/authenticated/{self.bucket_name}/{storage_path}"
        headers = self._headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 404:
                raise NotFoundException(f"File '{storage_path}' not found in Supabase Storage.")
            if resp.status_code != 200:
                raise ValidationException(f"Failed to download file from Supabase Storage: {resp.text}")
            return resp.content

    async def get_download_url(self, storage_path: str, expires_in: int = 3600) -> str:
        # Create a signed URL for secure download (SRS §25)
        url = f"{self.supabase_url}/storage/v1/object/sign/{self.bucket_name}/{storage_path}"
        headers = self._headers()
        payload = {"expiresIn": expires_in}

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                signed_path = resp.json().get("signedURL")
                return f"{self.supabase_url}/storage/v1{signed_path}"
            return f"/api/v1/attachments/file/{storage_path}"

    async def delete_file(self, storage_path: str) -> bool:
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}"
        headers = self._headers()
        payload = {"prefixes": [storage_path]}

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.request("DELETE", url, headers=headers, json=payload)
            return resp.status_code in [200, 204]
