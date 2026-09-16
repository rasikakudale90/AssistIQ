from backend.core.config import settings
from backend.providers.notifications.base import NotificationProvider
from backend.providers.notifications.gmail_smtp import GmailSmtpNotificationProvider
from backend.providers.notifications.brevo_http import BrevoNotificationProvider


def get_notification_provider() -> NotificationProvider:
    """
    Factory function returning the environment-appropriate notification provider (SRS §3.9).
    - Local: Gmail SMTP
    - Staging/Production: Brevo HTTP API
    """
    if settings.ENVIRONMENT == "local":
        return GmailSmtpNotificationProvider()
    return BrevoNotificationProvider()


__all__ = [
    "NotificationProvider",
    "GmailSmtpNotificationProvider",
    "BrevoNotificationProvider",
    "get_notification_provider",
]
