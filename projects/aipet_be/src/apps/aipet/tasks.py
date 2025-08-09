"""
Celery tasks for the aipet application.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_email_task(subject, message, recipient_list):
    """Send notification email asynchronously."""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        return f"Email sent successfully to {', '.join(recipient_list)}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
