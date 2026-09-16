from abc import ABC, abstractmethod
from typing import Optional


class NotificationProvider(ABC):
    """Abstract interface for all notification channels (SRS §3.9, §11)."""

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """
        Sends an email to the recipient.
        Returns True if sent successfully, False if failed.
        Failures must never crash the caller (SRS §3.9, §7.7).
        """
        pass
