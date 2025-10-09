"""
Notification Service
Handles in-app notifications and email sending with i18n support
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from services.i18n_service import get_translation
from services.email_service import send_report_email
from services.firebase_service import get_firestore_db

logger = logging.getLogger(__name__)

async def create_notification(
    student_id: str,
    notification_type: str,
    subject: str,
    body: str,
    language: str = "en",
    reason: Optional[str] = None,
    sender_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a notification record in Firebase
    
    Args:
        student_id: Student Firebase ID
        notification_type: 'inapp', 'email', or 'sms'
        subject: Notification subject
        body: Notification body
        language: Language code
        reason: Optional risk reason
        sender_id: Optional sender user ID
        metadata: Additional metadata
        
    Returns:
        Notification ID
    """
    try:
        db = get_firestore_db()
        if not db:
            logger.error("Firebase not initialized")
            return None
        
        notification_data = {
            "student_id": student_id,
            "type": notification_type,
            "subject": subject,
            "body": body,
            "language": language,
            "reason": reason,
            "sender_id": sender_id,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "sent_at": None,
            "read_at": None,
            "status": "pending"
        }
        
        # Add to notifications collection
        doc_ref = db.collection('notifications').add(notification_data)
        notification_id = doc_ref[1].id
        
        logger.info(f"Created notification {notification_id} for student {student_id}")
        return notification_id
        
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        return None


async def send_student_notification(
    student_data: Dict[str, Any],
    risk_level: str,
    reason: str,
    report_id: Optional[str] = None
) -> bool:
    """
    Send notification to a student about their risk status
    
    Args:
        student_data: Student information from Firebase
        risk_level: Risk level (Orange, Red)
        reason: Detailed reason for risk
        report_id: Optional simulation report ID
        
    Returns:
        True if notification sent successfully
    """
    try:
        language = student_data.get("language_preference", "en")
        
        # Get translated subject and body
        subject = get_translation("notification_subject", language)
        body_template = get_translation("notification_body", language)
        body = body_template.format(
            name=student_data.get("name", "Student"),
            reason=reason
        )
        
        # Create in-app notification
        notification_id = await create_notification(
            student_id=student_data.get("id"),
            notification_type="inapp",
            subject=subject,
            body=body,
            language=language,
            reason=reason
        )
        
        # Send email if student has email
        email_sent = False
        if student_data.get("email"):
            email_subject = get_translation("email_subject_student", language)
            email_body_template = get_translation("email_body_student", language)
            email_body = email_body_template.format(
                name=student_data.get("name", "Student"),
                reason=reason,
                institution=get_translation("institution_name", language)
            )
            
            # Attach report if available
            attachments = []
            if report_id:
                from pathlib import Path
                report_path = Path(__file__).parent.parent / "reports" / report_id / f"report_{language}.pdf"
                if report_path.exists():
                    attachments.append(str(report_path))
            
            email_sent = await send_report_email(
                recipient_email=student_data.get("email"),
                student_name=student_data.get("name", "Student"),
                risk_level=risk_level,
                report_paths=attachments,
                simulation_id=report_id or "N/A"
            )
        
        return notification_id is not None or email_sent
        
    except Exception as e:
        logger.error(f"Error sending student notification: {e}")
        return False


async def send_one_click_message(
    sender_id: str,
    recipient_ids: List[str],
    message: str,
    language: str = "en",
    channels: List[str] = ["inapp", "email"]
) -> Dict[str, int]:
    """
    Send one-click message from mentor to multiple students
    
    Args:
        sender_id: ID of sender (mentor/counselor)
        recipient_ids: List of student IDs
        message: Message to send
        language: Message language
        channels: List of channels to use
        
    Returns:
        Dictionary with success/failure counts
    """
    try:
        db = get_firestore_db()
        if not db:
            return {"success": 0, "failed": len(recipient_ids)}
        
        success_count = 0
        failed_count = 0
        
        for student_id in recipient_ids:
            try:
                # Get student data
                student_doc = db.collection('students').document(student_id).get()
                if not student_doc.exists:
                    failed_count += 1
                    continue
                
                student_data = student_doc.to_dict()
                
                # Create in-app notification
                if "inapp" in channels:
                    await create_notification(
                        student_id=student_id,
                        notification_type="inapp",
                        subject=get_translation("notification_risk_alert", language),
                        body=message,
                        language=language,
                        sender_id=sender_id
                    )
                
                # Send email
                if "email" in channels and student_data.get("email"):
                    await send_report_email(
                        recipient_email=student_data.get("email"),
                        student_name=student_data.get("name", "Student"),
                        risk_level="Info",
                        report_paths=[],
                        simulation_id="mentor_message"
                    )
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error sending message to student {student_id}: {e}")
                failed_count += 1
        
        logger.info(f"One-click message: {success_count} sent, {failed_count} failed")
        return {"success": success_count, "failed": failed_count}
        
    except Exception as e:
        logger.error(f"Error in one-click message: {e}")
        return {"success": 0, "failed": len(recipient_ids)}
