import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

from typing import Optional
from email.mime.application import MIMEApplication

async def send_assignment_email(recipient_email: str, recipient_name: str, task_title: str, task_details: str, deadline: str, attachment_data: Optional[bytes] = None, attachment_filename: Optional[str] = None):
    """
    Sends a high-fidelity operational assignment email via SMTP with optional attachment.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM
        msg['To'] = recipient_email
        msg['Subject'] = f"🚀 MISSION CRITICAL: {task_title}"

        body = f"""
        <html>
        <body style="font-family: 'Inter', sans-serif; background: #0a0a0c; color: #ffffff; padding: 2rem;">
            <div style="max-width: 600px; margin: auto; background: #121216; border: 1px solid #1a1a20; border-radius: 12px; padding: 30px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="display: inline-block; padding: 10px; background: rgba(0, 212, 255, 0.1); border-radius: 50%;">
                        <span style="font-size: 30px;">🛰️</span>
                    </div>
                </div>
                <h1 style="color: #00d4ff; font-size: 24px; text-align: center; margin-bottom: 20px; border-bottom: 1px solid rgba(0, 212, 255, 0.2); padding-bottom: 10px;">Operational Mission Deployment</h1>
                
                <p style="font-size: 16px; color: #e0e0e0;">Personnel: <strong>{recipient_name}</strong></p>
                <p style="font-size: 14px; color: #a0a0a0; line-height: 1.6;">A mission-critical objective has been authorized for your workstation. Please review the tactical details and associated documentation below.</p>
                
                <div style="background: rgba(255, 255, 255, 0.03); padding: 20px; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; color: #00d4ff; font-weight: bold; font-size: 18px;">{task_title}</p>
                    <p style="margin: 15px 0; color: #d0d0d0; line-height: 1.6; font-size: 14px;">{task_details}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255, 255, 255, 0.05);">
                        <p style="margin: 0; color: #ff3b5c; font-size: 12px; font-weight: 600;">DEADLINE: {deadline}</p>
                        <p style="margin: 0; color: #94a3b8; font-size: 10px; font-style: italic;">Reference ID: BG-{recipient_name[:3].upper()}-2026</p>
                    </div>
                </div>

                {f'<p style="font-size: 12px; color: #00d4ff;">📂 <strong>ATTACHED INTEL:</strong> {attachment_filename}</p>' if attachment_filename else ''}

                <p style="font-size: 13px; color: #808080; margin-top: 25px;">Operational continuity is paramount. Acknowledge this mission via the Guardian Secure Portal.</p>
                
                <hr style="border: none; border-top: 1px solid #2a2a30; margin: 30px 0;">
                <p style="text-align: center; font-size: 11px; color: #505050;">Burnout & Focus Guardian &copy; 2026 | Authorized Intelligence Services</p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        if attachment_data and attachment_filename:
            part = MIMEApplication(attachment_data, Name=attachment_filename)
            part['Content-Disposition'] = f'attachment; filename="{attachment_filename}"'
            msg.attach(part)

        logger.info(f"📧 [SIMULATED DISPATCH] To: {recipient_email} | Subject: {msg['Subject']} | Attachment: {attachment_filename or 'None'}")
        
        # SMTP logic deactivated per operator request
        # The following logs would match real dispatch:
        logger.info(f"💾 Mission data persisted. (Simulation mode: No external email sent to {recipient_email})")
        return True

    except Exception as e:
        logger.error(f"❌ Diagnostic Failure: {str(e)}")
        return False
