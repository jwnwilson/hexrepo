from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from datetime import timedelta


class EmailVerification(models.Model):
    """Model to store email verification tokens for new user registrations."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    def is_expired(self):
        """Check if the verification token has expired (24 hours)."""
        return timezone.now() > self.created_at + timedelta(hours=24)
    
    def verify(self):
        """Mark the verification as completed."""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.user.is_active = True
        self.user.save()
        self.save()
    
    def __str__(self):
        return f"Email verification for {self.user.username}"


class PasswordReset(models.Model):
    """Model to store password reset tokens."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)
    
    def is_expired(self):
        """Check if the reset token has expired (1 hour)."""
        return timezone.now() > self.created_at + timedelta(hours=1)
    
    def mark_as_used(self):
        """Mark the reset token as used."""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"Password reset for {self.user.username}"
