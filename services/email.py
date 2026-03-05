import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from core.config import settings

logger = logging.getLogger(__name__)

async def send_otp_email(email: str, otp: int) -> bool:
    """
    Send OTP via SMTP.
    Returns True if email was sent successfully.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        logger.warning(f"SMTP credentials not configured. OTP for {email}: {otp}")
        return False

    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_FROM
    msg['To'] = email
    msg['Subject'] = f"{otp} is your ShowGo OTP"

    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #0B0B15; color: #FFFFFF;">
            <div style="max-width: 600px; margin: auto; background-color: #1F1F2E; padding: 30px; border-radius: 12px; border: 1px solid #8A2BE2;">
                <h2 style="color: #A855F7; text-align: center;">ShowGo OTP</h2>
                <p style="font-size: 16px; text-align: center;">Use the code below to sign in to your account.</p>
                <div style="background-color: #0B0B15; padding: 20px; border-radius: 8px; text-align: center; margin: 30px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #FFF;">{otp}</span>
                </div>
                <p style="font-size: 12px; color: #9CA3AF; text-align: center;">This code will expire in 5 minutes. Do not share it with anyone.</p>
            </div>
        </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    try:
        # SMTP_SSL for port 465, starttls for 587
        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg)
        server.quit()
        logger.info(f"OTP Email sent to {email}")
    except Exception as e:
        logger.error(f"SMTP failed to send email: {e}")
        return False

from email.mime.application import MIMEApplication
import os

async def send_ticket_email(email: str, pdf_path: str, movie_title: str) -> bool:
    """
    Send Booking Ticket PDF via SMTP.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        logger.warning(f"SMTP not configured. Could not send ticket for {movie_title} to {email}")
        return False

    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_FROM
    msg['To'] = email
    msg['Subject'] = f"Your Ticket for {movie_title} - ShowGo"

    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #0B0B15; color: #FFFFFF;">
            <div style="max-width: 600px; margin: auto; background-color: #1F1F2E; padding: 30px; border-radius: 12px; border: 1px solid #8A2BE2;">
                <h2 style="color: #A855F7; text-align: center;">Ticket Confirmed!</h2>
                <p style="font-size: 16px; text-align: center;">Enjoy your movie! Your ticket for <b>{movie_title}</b> is attached to this email.</p>
                <p style="font-size: 14px; color: #9CA3AF; text-align: center; margin-top: 20px;">
                    Please present the attached PDF at the cinema hall entrance.
                </p>
            </div>
        </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    # Attach PDF
    try:
        with open(pdf_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            msg.attach(part)
    except Exception as e:
        logger.error(f"Failed to attach PDF: {e}")
        return False

    try:
        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg)
        server.quit()
        logger.info(f"Ticket Email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"SMTP failed to send ticket email: {e}")
        return False
