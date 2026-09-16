from backend.core.config import settings
from backend.providers.storage.base import StorageProvider
from backend.providers.storage.local_storage import LocalStorageProvider
from backend.providers.storage.supabase_storage import SupabaseStorageProvider


def get_storage_provider() -> StorageProvider:
    """
    Factory function returning the environment-appropriate storage provider (SRS §3.1).
    - Local: LocalStorageProvider (uploads/ directory)
    - Staging/Production: SupabaseStorageProvider
    """
    if settings.ENVIRONMENT == "local" or not settings.SUPABASE_URL:
        return LocalStorageProvider()
    return SupabaseStorageProvider()


__all__ = [
    "StorageProvider",
    "LocalStorageProvider",
    "SupabaseStorageProvider",
    "get_storage_provider",
]
