"""
Email Service
Sends simulation reports via email using FastAPI-Mail
"""

import os
import logging
from typing import List, Optional
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

logger = logging.getLogger(__name__)

# Email configuration from environment variables
def get_email_config() -> Optional[ConnectionConfig]:
    """
    Get email configuration from environment variables
    
    Environment variables needed:
    - MAIL_USERNAME: Email address to send from
    - MAIL_PASSWORD: Email password or app password
    - MAIL_SERVER: SMTP server (default: smtp.gmail.com)
    - MAIL_PORT: SMTP port (default: 587)
    """
    try:
        mail_username = os.getenv("MAIL_USERNAME")
        mail_password = os.getenv("MAIL_PASSWORD")
        
        if not mail_username or not mail_password:
            logger.warning("Email credentials not configured. Email sending will be disabled.")
            logger.warning("Set MAIL_USERNAME and MAIL_PASSWORD environment variables to enable email.")
            return None
        
        conf = ConnectionConfig(
            MAIL_USERNAME=mail_username,
            MAIL_PASSWORD=mail_password,
            MAIL_FROM=mail_username,
            MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
            MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        
        logger.info(f"Email service configured with {mail_username}")
        return conf
        
    except Exception as e:
        logger.error(f"Error configuring email service: {e}")
        return None


# Initialize email configuration
EMAIL_CONFIG = get_email_config()


async def send_report_email(
    recipient_email: str,
    student_name: str,
    risk_level: str,
    report_paths: List[str],
    simulation_id: str
) -> bool:
    """
    Send simulation report via email with PDF attachments
    
    Args:
        recipient_email: Email address to send to
        student_name: Name or enrollment number of student
        risk_level: Final risk assessment (Green/Yellow/Orange/Red)
        report_paths: List of PDF file paths to attach
        simulation_id: Unique simulation identifier
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if not EMAIL_CONFIG:
        logger.warning("Email service not configured. Cannot send email.")
        return False
    
    try:
        # Prepare email body based on risk level
        risk_messages = {
            "Green": "The student is performing well with minimal dropout risk.",
            "Yellow": "The student shows some warning signs and requires monitoring.",
            "Orange": "The student is at high risk and requires immediate intervention.",
            "Red": "The student is at critical risk and needs urgent attention."
        }
        
        risk_message = risk_messages.get(risk_level, "Risk assessment completed.")
        
        # Create HTML email body
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #1e40af; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .risk-box {{ 
                        padding: 15px; 
                        margin: 20px 0; 
                        border-radius: 8px; 
                        text-align: center;
                        font-size: 18px;
                        font-weight: bold;
                    }}
                    .risk-Green {{ background-color: #22c55e; color: white; }}
                    .risk-Yellow {{ background-color: #eab308; color: white; }}
                    .risk-Orange {{ background-color: #f97316; color: white; }}
                    .risk-Red {{ background-color: #ef4444; color: white; }}
                    .footer {{ 
                        margin-top: 30px; 
                        padding-top: 20px; 
                        border-top: 1px solid #ddd; 
                        font-size: 12px; 
                        color: #666;
                        text-align: center;
                    }}
                    .attachments {{ 
                        background-color: #f3f4f6; 
                        padding: 15px; 
                        border-radius: 8px; 
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Dropout Risk Assessment Report</h1>
                    <p>AI-Based Student Risk Prediction System</p>
                </div>
                
                <div class="content">
                    <p>Dear Sir/Madam,</p>
                    
                    <p>This email contains the dropout risk assessment report for student <strong>{student_name}</strong>.</p>
                    
                    <div class="risk-box risk-{risk_level}">
                        Risk Level: {risk_level.upper()}
                    </div>
                    
                    <p><strong>Assessment Summary:</strong><br>
                    {risk_message}</p>
                    
                    <div class="attachments">
                        <h3>📎 Attached Reports</h3>
                        <p>This email includes detailed reports in three languages:</p>
                        <ul>
                            <li><strong>English</strong> (report_en.pdf)</li>
                            <li><strong>Hindi</strong> (report_hi.pdf - हिंदी)</li>
                            <li><strong>Rajasthani</strong> (report_rj.pdf - राजस्थानी)</li>
                        </ul>
                        <p>Please review the attached PDF reports for complete details and recommendations.</p>
                    </div>
                    
                    <p><strong>Simulation ID:</strong> {simulation_id}</p>
                    
                    <p>If you have any questions or need further assistance, please contact the administration.</p>
                    
                    <div class="footer">
                        <p><strong>CONFIDENTIAL - For Official Use Only</strong></p>
                        <p>Generated by AI-Based Dropout Prediction System</p>
                        <p>Government of Rajasthan - Department of Technical Education</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
Dropout Risk Assessment Report
AI-Based Student Risk Prediction System

Dear Sir/Madam,

This email contains the dropout risk assessment report for student {student_name}.

Risk Level: {risk_level.upper()}

Assessment Summary:
{risk_message}

This email includes detailed reports in three languages:
- English (report_en.pdf)
- Hindi (report_hi.pdf - हिंदी)
- Rajasthani (report_rj.pdf - राजस्थानी)

Please review the attached PDF reports for complete details and recommendations.

Simulation ID: {simulation_id}

If you have any questions or need further assistance, please contact the administration.

---
CONFIDENTIAL - For Official Use Only
Generated by AI-Based Dropout Prediction System
Government of Rajasthan - Department of Technical Education
        """
        
        # Prepare attachments
        attachments = []
        for report_path in report_paths:
            if Path(report_path).exists():
                attachments.append(report_path)
            else:
                logger.warning(f"Report file not found: {report_path}")
        
        if not attachments:
            logger.error("No valid report files found to attach")
            return False
        
        # Create message
        message = MessageSchema(
            subject=f"Dropout Risk Assessment Report - {student_name} [{risk_level} Risk]",
            recipients=[recipient_email],
            body=text_body,
            html=html_body,
            subtype=MessageType.html,
            attachments=attachments
        )
        
        # Send email
        fm = FastMail(EMAIL_CONFIG)
        await fm.send_message(message)
        
        logger.info(f"Report email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {e}")
        return False


async def send_test_email(recipient_email: str) -> bool:
    """
    Send a test email to verify email configuration
    
    Args:
        recipient_email: Email address to send test email to
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if not EMAIL_CONFIG:
        logger.warning("Email service not configured. Cannot send test email.")
        return False
    
    try:
        html_body = """
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Email Service Test</h2>
                <p>This is a test email from the AI-Based Dropout Prediction System.</p>
                <p>If you received this email, the email service is configured correctly! ✅</p>
                <hr>
                <p style="font-size: 12px; color: #666;">
                    AI-Based Dropout Prediction System<br>
                    Government of Rajasthan - Department of Technical Education
                </p>
            </body>
        </html>
        """
        
        message = MessageSchema(
            subject="Test Email - Dropout Prediction System",
            recipients=[recipient_email],
            body="This is a test email from the AI-Based Dropout Prediction System.",
            html=html_body,
            subtype=MessageType.html
        )
        
        fm = FastMail(EMAIL_CONFIG)
        await fm.send_message(message)
        
        logger.info(f"Test email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send test email: {e}")
        return False


def is_email_configured() -> bool:
    """Check if email service is properly configured"""
    return EMAIL_CONFIG is not None
