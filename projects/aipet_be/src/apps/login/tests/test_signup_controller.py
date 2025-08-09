"""
Tests for the login app models and controllers.
"""

import json
import uuid
from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.login.models import EmailVerification, PasswordReset


class EmailVerificationModelTest(TestCase):
    """Test EmailVerification model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_active=False,
        )

    def test_email_verification_creation(self):
        """Test creating an email verification record."""
        verification = EmailVerification.objects.create(user=self.user)

        self.assertIsInstance(verification.token, uuid.UUID)
        self.assertFalse(verification.is_verified)
        self.assertIsNone(verification.verified_at)
        self.assertIsNotNone(verification.created_at)
        self.assertEqual(
            str(verification), f"Email verification for {self.user.username}"
        )

    def test_is_expired_not_expired(self):
        """Test that a recent verification is not expired."""
        verification = EmailVerification.objects.create(user=self.user)
        self.assertFalse(verification.is_expired())

    def test_is_expired_when_expired(self):
        """Test that an old verification is expired."""
        verification = EmailVerification.objects.create(user=self.user)
        # Manually set created_at to 25 hours ago
        verification.created_at = timezone.now() - timedelta(hours=25)
        verification.save()

        self.assertTrue(verification.is_expired())

    def test_verify_method(self):
        """Test the verify method activates user and marks as verified."""
        verification = EmailVerification.objects.create(user=self.user)
        self.assertFalse(self.user.is_active)
        self.assertFalse(verification.is_verified)

        verification.verify()

        # Refresh user from database
        self.user.refresh_from_db()
        verification.refresh_from_db()

        self.assertTrue(self.user.is_active)
        self.assertTrue(verification.is_verified)
        self.assertIsNotNone(verification.verified_at)


class PasswordResetModelTest(TestCase):
    """Test PasswordReset model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_password_reset_creation(self):
        """Test creating a password reset record."""
        reset = PasswordReset.objects.create(user=self.user)

        self.assertIsInstance(reset.token, uuid.UUID)
        self.assertFalse(reset.is_used)
        self.assertIsNone(reset.used_at)
        self.assertIsNotNone(reset.created_at)
        self.assertEqual(str(reset), f"Password reset for {self.user.username}")

    def test_is_expired_not_expired(self):
        """Test that a recent reset token is not expired."""
        reset = PasswordReset.objects.create(user=self.user)
        self.assertFalse(reset.is_expired())

    def test_is_expired_when_expired(self):
        """Test that an old reset token is expired."""
        reset = PasswordReset.objects.create(user=self.user)
        # Manually set created_at to 2 hours ago
        reset.created_at = timezone.now() - timedelta(hours=2)
        reset.save()

        self.assertTrue(reset.is_expired())

    def test_mark_as_used(self):
        """Test marking a reset token as used."""
        reset = PasswordReset.objects.create(user=self.user)
        self.assertFalse(reset.is_used)
        self.assertIsNone(reset.used_at)

        reset.mark_as_used()

        self.assertTrue(reset.is_used)
        self.assertIsNotNone(reset.used_at)

    def test_multiple_reset_tokens_per_user(self):
        """Test that a user can have multiple reset tokens."""
        reset1 = PasswordReset.objects.create(user=self.user)
        reset2 = PasswordReset.objects.create(user=self.user)

        self.assertEqual(PasswordReset.objects.filter(user=self.user).count(), 2)
        self.assertNotEqual(reset1.token, reset2.token)


@pytest.mark.django_db
class TestSignupController:
    """Test SignupController API endpoints."""

    def test_signup_success(self, api_client, sample_user_data, mailbox):
        """Test successful user signup."""
        response = api_client.post_json("/api/v1/auth/signup", sample_user_data)

        assert response.status_code == 200
        data = json.loads(response.content)

        assert data["verification_required"] is True
        assert "verification link" in data["message"]
        assert data["user_id"] > 0

        # Check user was created but inactive
        user = User.objects.get(username=sample_user_data["username"])
        assert not user.is_active
        assert user.email == sample_user_data["email"]

        # Check verification record was created
        verification = EmailVerification.objects.get(user=user)
        assert not verification.is_verified

        # Check email was sent
        assert len(mailbox) == 1
        assert sample_user_data["email"] in mailbox[0].to

    def test_signup_duplicate_username(
        self, api_client, sample_user_data, user_factory
    ):
        """Test signup with duplicate username."""
        # Create existing user
        user_factory(username=sample_user_data["username"])

        response = api_client.post_json("/api/v1/auth/signup", sample_user_data)

        assert response.status_code == 200
        data = json.loads(response.content)

        assert data["verification_required"] is False
        assert "Username already exists" in data["message"]
        assert data["user_id"] == 0
