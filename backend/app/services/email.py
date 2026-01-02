"""Email service for sending transactional emails.

This is a placeholder implementation that logs emails instead of sending them.
Replace with actual email provider (SendGrid, AWS SES, SMTP, etc.) in production.
"""

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending transactional emails.

    This is a placeholder implementation. In production, integrate with:
    - SendGrid
    - AWS SES
    - Mailgun
    - SMTP server
    """

    def __init__(self) -> None:
        """Initialize email service."""
        self.from_email = "noreply@example.com"
        self.from_name = "Enterprise Boilerplate"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> bool:
        """
        Send an email.

        Args:
            to_email: Recipient email address.
            subject: Email subject.
            html_content: HTML content of the email.
            text_content: Plain text content (optional).

        Returns:
            bool: True if email was sent successfully.
        """
        # Placeholder: Log email instead of sending
        logger.info(
            f"[EMAIL] To: {to_email}\n"
            f"Subject: {subject}\n"
            f"Content: {html_content[:200]}..."
        )

        if settings.is_development:
            print("=" * 60)
            print("📧 EMAIL (Development Mode - Not Actually Sent)")
            print("=" * 60)
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print("-" * 60)
            print(html_content)
            print("=" * 60)

        # TODO: Implement actual email sending
        # Example with SendGrid:
        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail
        #
        # message = Mail(
        #     from_email=self.from_email,
        #     to_emails=to_email,
        #     subject=subject,
        #     html_content=html_content,
        # )
        # sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        # response = sg.send(message)
        # return response.status_code == 202

        return True

    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        username: str,
    ) -> bool:
        """
        Send password reset email.

        Args:
            to_email: Recipient email address.
            reset_token: Password reset token.
            username: User's username.

        Returns:
            bool: True if email was sent successfully.
        """
        # Build reset URL
        # In production, this should be the frontend URL
        reset_url = f"http://localhost:3000/auth/reset-password?token={reset_token}"

        subject = "Password Reset Request"
        html_content = get_password_reset_template(
            username=username,
            reset_url=reset_url,
        )

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
        )

    async def send_welcome_email(
        self,
        to_email: str,
        username: str,
    ) -> bool:
        """
        Send welcome email after registration.

        Args:
            to_email: Recipient email address.
            username: User's username.

        Returns:
            bool: True if email was sent successfully.
        """
        subject = "Welcome to Enterprise Boilerplate"
        html_content = get_welcome_template(username=username)

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
        )

    async def send_email_verification(
        self,
        to_email: str,
        verification_token: str,
        username: str,
    ) -> bool:
        """
        Send email verification email.

        Args:
            to_email: Recipient email address.
            verification_token: Email verification token.
            username: User's username.

        Returns:
            bool: True if email was sent successfully.
        """
        # Build verification URL
        verify_url = f"http://localhost:3000/auth/verify-email?token={verification_token}"

        subject = "Verify Your Email Address"
        html_content = get_email_verification_template(
            username=username,
            verify_url=verify_url,
        )

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
        )


def get_password_reset_template(username: str, reset_url: str) -> str:
    """Generate password reset email HTML template."""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: #f9fafb;
            border-radius: 8px;
            padding: 32px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 24px;
        }}
        .header h1 {{
            color: #1f2937;
            font-size: 24px;
            margin: 0;
        }}
        .content {{
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .button {{
            display: inline-block;
            background: #3b82f6;
            color: white;
            padding: 12px 24px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            margin: 16px 0;
        }}
        .button:hover {{
            background: #2563eb;
        }}
        .footer {{
            text-align: center;
            color: #6b7280;
            font-size: 14px;
        }}
        .warning {{
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 6px;
            padding: 12px;
            margin-top: 16px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Password Reset Request</h1>
        </div>
        <div class="content">
            <p>Hello <strong>{username}</strong>,</p>
            <p>We received a request to reset your password. Click the button below to create a new password:</p>
            <p style="text-align: center;">
                <a href="{reset_url}" class="button">Reset Password</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #3b82f6;">{reset_url}</p>
            <div class="warning">
                ⚠️ This link will expire in 30 minutes. If you didn't request a password reset, 
                please ignore this email or contact support if you have concerns.
            </div>
        </div>
        <div class="footer">
            <p>This email was sent by Enterprise Boilerplate</p>
            <p>© 2024 Enterprise Boilerplate. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


def get_welcome_template(username: str) -> str:
    """Generate welcome email HTML template."""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: #f9fafb;
            border-radius: 8px;
            padding: 32px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 24px;
        }}
        .header h1 {{
            color: #1f2937;
            font-size: 24px;
            margin: 0;
        }}
        .content {{
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .footer {{
            text-align: center;
            color: #6b7280;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome to Enterprise Boilerplate!</h1>
        </div>
        <div class="content">
            <p>Hello <strong>{username}</strong>,</p>
            <p>Thank you for creating an account. We're excited to have you on board!</p>
            <p>You can now:</p>
            <ul>
                <li>Access your dashboard</li>
                <li>Manage your documents</li>
                <li>Configure your settings</li>
            </ul>
            <p>If you have any questions, feel free to reach out to our support team.</p>
        </div>
        <div class="footer">
            <p>This email was sent by Enterprise Boilerplate</p>
            <p>© 2024 Enterprise Boilerplate. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


def get_email_verification_template(username: str, verify_url: str) -> str:
    """Generate email verification HTML template."""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Email</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: #f9fafb;
            border-radius: 8px;
            padding: 32px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 24px;
        }}
        .header h1 {{
            color: #1f2937;
            font-size: 24px;
            margin: 0;
        }}
        .content {{
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .button {{
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 12px 24px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            margin: 16px 0;
        }}
        .footer {{
            text-align: center;
            color: #6b7280;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✉️ Verify Your Email</h1>
        </div>
        <div class="content">
            <p>Hello <strong>{username}</strong>,</p>
            <p>Please verify your email address by clicking the button below:</p>
            <p style="text-align: center;">
                <a href="{verify_url}" class="button">Verify Email</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #10b981;">{verify_url}</p>
        </div>
        <div class="footer">
            <p>This email was sent by Enterprise Boilerplate</p>
            <p>© 2024 Enterprise Boilerplate. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


# Global email service instance
email_service = EmailService()
