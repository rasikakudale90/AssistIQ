import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from backend.core.config import settings
from backend.providers.notifications.base import NotificationProvider

logger = logging.getLogger("assistiq.notifications.gmail")


class GmailSmtpNotificationProvider(NotificationProvider):
    """
    Gmail SMTP implementation for local development (SRS §3.9).
    Uses free Gmail account + app password.
    """

    def __init__(
        self,
        smtp_address: Optional[str] = None,
        smtp_app_password: Optional[str] = None,
    ):
        self.smtp_address = smtp_address or settings.GMAIL_SMTP_ADDRESS
        self.smtp_app_password = smtp_app_password or settings.GMAIL_SMTP_APP_PASSWORD

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        if not self.smtp_address or not self.smtp_app_password:
            logger.warning(f"[LOCAL DEV MOCK] Email to <{to_email}> - Subject: '{subject}'\nContent:\n{text_body or html_body}")
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"AssistIQ <{self.smtp_address}>"
            msg["To"] = to_email

            if text_body:
                msg.attach(MIMEText(text_body, "plain", "utf-8"))
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_address, self.smtp_app_password)
                server.sendmail(self.smtp_address, [to_email], msg.as_string())

            logger.info(f"Email successfully sent to {to_email} via Gmail SMTP.")
            return True
        except Exception as exc:
            logger.error(f"Failed to send email to {to_email} via Gmail SMTP: {exc}")
            return False
