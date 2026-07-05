"""Email notification service using aiosmtplib."""

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class EmailService:
    """Send emails via SMTP."""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_name = settings.SMTP_FROM_NAME
        self.from_email = settings.SMTP_FROM_EMAIL
        self.use_tls = settings.SMTP_USE_TLS

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        """Send an email."""
        if not self.username or not self.password:
            logger.warning("smtp_not_configured", to=to_email, subject=subject)
            return False

        try:
            import aiosmtplib

            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            if text_body:
                msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls,
            )

            logger.info("email_sent", to=to_email, subject=subject)
            return True

        except Exception as e:
            logger.error("email_send_failed", to=to_email, error=str(e))
            return False

    async def send_leave_notification(
        self,
        to_email: str,
        employee_name: str,
        leave_type: str,
        status: str,
        start_date: str,
        end_date: str,
    ) -> bool:
        """Send leave status notification email."""
        color = "#10b981" if status == "approved" else "#ef4444"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #1e1b4b; padding: 20px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0;">SynapseHR</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border: 1px solid #e2e8f0;">
                <h2 style="color: #1e293b;">Leave Request {status.title()}</h2>
                <p style="color: #475569;">Dear {employee_name},</p>
                <p style="color: #475569;">Your {leave_type} request has been <strong style="color: {color};">{status}</strong>.</p>
                <div style="background: white; padding: 15px; border-radius: 6px; margin: 15px 0; border: 1px solid #e2e8f0;">
                    <p style="margin: 5px 0; color: #64748b;"><strong>Period:</strong> {start_date} to {end_date}</p>
                    <p style="margin: 5px 0; color: #64748b;"><strong>Status:</strong> <span style="color: {color};">{status.title()}</span></p>
                </div>
                <p style="color: #94a3b8; font-size: 12px;">This is an automated notification from SynapseHR.</p>
            </div>
        </div>
        """
        return await self.send_email(to_email, f"Leave Request {status.title()}", html)

    async def send_welcome_email(self, to_email: str, employee_name: str, temp_password: str) -> bool:
        """Send welcome email to new employee."""
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #1e1b4b; padding: 20px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; margin: 0;">Welcome to SynapseHR</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border: 1px solid #e2e8f0;">
                <h2 style="color: #1e293b;">Hello {employee_name}!</h2>
                <p style="color: #475569;">Your account has been created. Here are your login credentials:</p>
                <div style="background: white; padding: 15px; border-radius: 6px; margin: 15px 0; border: 1px solid #e2e8f0;">
                    <p style="margin: 5px 0; color: #64748b;"><strong>Email:</strong> {to_email}</p>
                    <p style="margin: 5px 0; color: #64748b;"><strong>Temporary Password:</strong> {temp_password}</p>
                </div>
                <p style="color: #ef4444; font-size: 13px;">Please change your password after first login.</p>
                <p style="color: #94a3b8; font-size: 12px;">This is an automated notification from SynapseHR.</p>
            </div>
        </div>
        """
        return await self.send_email(to_email, "Welcome to SynapseHR", html)


email_service = EmailService()
