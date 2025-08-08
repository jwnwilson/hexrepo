# User Signup and Verification API

This document describes the new user signup and email verification endpoints added to the AI Pet Django-Ninja application.

## Overview

The signup system includes:
- User registration with email verification
- Email verification via token
- Resend verification email functionality

## API Endpoints

### 1. User Signup
**POST** `/api/v1/auth/signup`

Register a new user account. The user will be created but inactive until email verification is completed.

**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com", 
    "password": "secure_password123",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response:**
```json
{
    "message": "User registered successfully. Please check your email for verification link.",
    "user_id": 123,
    "verification_required": true
}
```

**Error Responses:**
- Username already exists
- Email already registered
- Password validation failed

### 2. Email Verification
**GET** `/api/v1/auth/verify/{token}`

Verify user email address using the verification token sent via email.

**Parameters:**
- `token`: UUID verification token from email

**Response:**
```json
{
    "message": "Email verified successfully. Your account is now active.",
    "verified": true
}
```

**Error Responses:**
- Invalid or expired verification token
- Email already verified
- Token expired (24 hours)

### 3. Resend Verification Email
**POST** `/api/v1/auth/resend-verification`

Resend verification email for a user who hasn't verified their email yet.

**Request Body:**
```json
{
    "email": "john@example.com"
}
```

**Response:**
```json
{
    "message": "Verification email sent. Please check your email.",
    "user_id": 123,
    "verification_required": true
}
```

## Email Configuration

### Development
In development mode, emails are printed to the console for testing.

### Production
For production, update the email settings in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Database Models

### EmailVerification Model
- `user`: OneToOneField to Django User model
- `token`: UUID field for verification token
- `created_at`: Creation timestamp
- `verified_at`: Verification timestamp (null until verified)
- `is_verified`: Boolean verification status
- `is_expired()`: Method to check if token expired (24 hours)
- `verify()`: Method to mark verification as complete and activate user

## Integration with Existing Authentication

The signup system works alongside the existing `ninja_jwt` authentication. Once a user is verified, they can use the existing JWT login endpoints to authenticate.

## Testing

To test the signup flow:

1. **Register a new user:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/signup \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "securepass123",
       "first_name": "Test",
       "last_name": "User"
     }'
   ```

2. **Check console for verification email** (development mode)

3. **Verify email using token from email:**
   ```bash
   curl -X GET http://localhost:8000/api/v1/auth/verify/{token}
   ```

4. **Login using existing JWT endpoints** (user is now active)