"""
Tests for signup functionality.
"""
import pytest
import json
from unittest.mock import patch
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from ..models import EmailVerification


@pytest.mark.django_db
class TestSignupEndpoints:
    """Test SignupController signup-related endpoints."""
    
    def test_signup_success(self, api_client, sample_user_data, mailbox):
        """Test successful user signup."""
        response = api_client.post_json('/api/v1/auth/signup', sample_user_data)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        assert data['verification_required'] is True
        assert 'verification link' in data['message']
        assert data['user_id'] > 0
        
        # Check user was created but inactive
        user = User.objects.get(username=sample_user_data['username'])
        assert not user.is_active
        assert user.email == sample_user_data['email']
        
        # Check verification record was created
        verification = EmailVerification.objects.get(user=user)
        assert not verification.is_verified
        
        # Check email was sent
        assert len(mailbox) == 1
        assert sample_user_data['email'] in mailbox[0].to
    
    def test_signup_duplicate_username(self, api_client, sample_user_data, user_factory):
        """Test signup with duplicate username."""
        # Create existing user
        user_factory(username=sample_user_data['username'])
        
        response = api_client.post_json('/api/v1/auth/signup', sample_user_data)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        assert data['verification_required'] is False
        assert 'Username already exists' in data['message']
        assert data['user_id'] == 0
    
    def test_signup_duplicate_email(self, api_client, sample_user_data, user_factory):
        """Test signup with duplicate email."""
        # Create existing user with same email
        user_factory(email=sample_user_data['email'])
        
        response = api_client.post_json('/api/v1/auth/signup', sample_user_data)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        assert data['verification_required'] is False
        assert 'Email already registered' in data['message']
        assert data['user_id'] == 0
    
    def test_signup_weak_password(self, api_client, sample_user_data):
        """Test signup with weak password."""
        sample_user_data['password'] = '123'  # Too weak
        
        response = api_client.post_json('/api/v1/auth/signup', sample_user_data)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        assert data['verification_required'] is False
        assert 'Password validation failed' in data['message']
        assert data['user_id'] == 0
    
    @patch('apps.login.controllers.login.SignupController._send_verification_email')
    def test_signup_email_failure(self, mock_send_email, api_client, sample_user_data):
        """Test signup when email sending fails."""
        mock_send_email.side_effect = Exception("Email failed")
        
        response = api_client.post_json('/api/v1/auth/signup', sample_user_data)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        assert data['verification_required'] is False
        assert 'error occurred during registration' in data['message']
        assert data['user_id'] == 0


@pytest.mark.django_db 
class TestEmailVerificationEndpoints:
    """Test email verification endpoints."""
    
    def test_verify_email_success(self, api_client, user_factory):
        """Test successful email verification."""
        # Create inactive user with verification
        user = user_factory(is_active=False)
        verification = EmailVerification.objects.create(user=user)
        
        response = api_client.get(f'/api/v1/auth/verify/{verification.token}')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        assert data['verified'] is True
        assert 'successfully' in data['message']
        
        # Check user is now active
        user.refresh_from_db()
        verification.refresh_from_db()
        assert user.is_active
        assert verification.is_verified
    
    def test_verify_email_invalid_token(self, api_client, uuid_token):
        """Test email verification with invalid token."""
        response = api_client.get(f'/api/v1/auth/verify/{uuid_token}')
        
        assert response.status_code == 404  # get_object_or_404 returns 404
    
    def test_verify_email_already_verified(self, api_client, user_factory):
        """Test verifying already verified email."""
        user = user_factory(is_active=True)
        verification = EmailVerification.objects.create(user=user, is_verified=True)
        
        response = api_client.get(f'/api/v1/auth/verify/{verification.token}')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        assert data['verified'] is True
        assert 'already verified' in data['message']
    
    def test_verify_email_expired_token(self, api_client, user_factory):
        """Test verifying with expired token."""
        user = user_factory(is_active=False)
        verification = EmailVerification.objects.create(user=user)
        
        # Make token expired
        verification.created_at = timezone.now() - timedelta(hours=25)
        verification.save()
        
        response = api_client.get(f'/api/v1/auth/verify/{verification.token}')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        assert data['verified'] is False
        assert 'expired' in data['message']
    
    def test_resend_verification_success(self, api_client, user_factory, mailbox):
        """Test successful verification email resend."""
        user = user_factory(is_active=False)
        EmailVerification.objects.create(user=user)
        
        response = api_client.post_json(
            '/api/v1/auth/resend-verification',
            {'email': user.email}
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        assert data['verification_required'] is True
        assert 'email sent' in data['message']
        assert len(mailbox) == 1
    
    def test_resend_verification_already_verified(self, api_client, user_factory):
        """Test resending verification for already verified user."""
        user = user_factory(is_active=True)
        
        response = api_client.post_json(
            '/api/v1/auth/resend-verification',
            {'email': user.email}
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        assert data['verification_required'] is False
        assert 'already verified' in data['message']
    
    def test_resend_verification_nonexistent_user(self, api_client):
        """Test resending verification for non-existent user."""
        response = api_client.post_json(
            '/api/v1/auth/resend-verification',
            {'email': 'nonexistent@example.com'}
        )
        
        assert response.status_code == 404  # get_object_or_404 returns 404