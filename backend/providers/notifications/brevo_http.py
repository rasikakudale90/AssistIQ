import logging
from typing import Optional
import httpx

from backend.core.config import settings
from backend.providers.notifications.base import NotificationProvider

logger = logging.getLogger("assistiq.notifications.brevo")


class BrevoNotificationProvider(NotificationProvider):
    """
    Brevo HTTP API implementation for staging and production (SRS §3.9).
    Sends over HTTPS port 443 to avoid Render SMTP port blocking.
    """

    BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.BREVO_API_KEY
        self.sender_email = settings.BREVO_SENDER_EMAIL
        self.sender_name = settings.BREVO_SENDER_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        if not self.api_key:
            logger.warning(f"[BREVO MOCK] Email to <{to_email}> - Subject: '{subject}'")
            return True

        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json",
        }
        payload = {
            "sender": {"name": self.sender_name, "email": self.sender_email},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_body,
        }
        if text_body:
            payload["textContent"] = text_body

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.BREVO_API_URL, headers=headers, json=payload)
                if response.status_code in [200, 201, 202]:
                    logger.info(f"Email successfully sent to {to_email} via Brevo HTTP API.")
                    return True
                else:
                    logger.error(f"Brevo API error ({response.status_code}): {response.text}")
                    return False
        except Exception as exc:
            logger.error(f"Failed to send email to {to_email} via Brevo API: {exc}")
            return False
