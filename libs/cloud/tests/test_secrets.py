import os
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from hexrepo_cloud.secrets import AWSSecretAdaptor


@pytest.fixture
def aws_secret_adaptor():
    with patch("boto3.client"):
        adaptor = AWSSecretAdaptor()
        adaptor.client = MagicMock()
        return adaptor


def test_get_secret(aws_secret_adaptor):
    """Test getting a secret from AWS Secrets Manager"""
    secret_name = "test-secret"
    secret_value = "test-value"
    aws_secret_adaptor.client.get_secret_value.return_value = {
        "SecretString": secret_value
    }

    result = aws_secret_adaptor.get_secret(secret_name)
    assert result == secret_value
    aws_secret_adaptor.client.get_secret_value.assert_called_once_with(
        SecretId=secret_name
    )


def test_get_secret_not_found(aws_secret_adaptor):
    """Test getting a non-existent secret"""
    secret_name = "nonexistent-secret"
    aws_secret_adaptor.client.get_secret_value.side_effect = ClientError(
        {"Error": {"Code": "ResourceNotFoundException"}}, "GetSecretValue"
    )

    with pytest.raises(ClientError) as exc_info:
        aws_secret_adaptor.get_secret(secret_name)
    assert "ResourceNotFoundException" in str(exc_info.value)


def test_secret_cache_non_aws(aws_secret_adaptor):
    """Test secret caching outside AWS Lambda environment"""
    secret_name = "test-secret"
    secret_value = "test-value"

    # Ensure we're not in AWS Lambda environment
    with patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_NAME": ""}):
        # First call should fetch from AWS
        aws_secret_adaptor.client.get_secret_value.return_value = {
            "SecretString": secret_value
        }
        result = aws_secret_adaptor.get_secret(secret_name)
        assert result == secret_value
        aws_secret_adaptor.client.get_secret_value.assert_called_once()

        # Reset mock for second call
        aws_secret_adaptor.client.get_secret_value.reset_mock()

        # Second call should still fetch from AWS (no caching)
        result = aws_secret_adaptor.get_secret(secret_name)
        assert result == secret_value
        aws_secret_adaptor.client.get_secret_value.assert_called_once()


def test_secret_cache_write_error(aws_secret_adaptor):
    """Test handling cache write errors in AWS Lambda"""
    secret_name = "test-secret"
    secret_value = "test-value"

    # Mock AWS Lambda environment
    with patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_NAME": "test-function"}):
        # Mock file operations to raise an error
        with patch("builtins.open", side_effect=IOError("Write error")):
            aws_secret_adaptor.client.get_secret_value.return_value = {
                "SecretString": secret_value
            }

            # Should still return the secret even if cache write fails
            result = aws_secret_adaptor.get_secret(secret_name)
            assert result == secret_value
            aws_secret_adaptor.client.get_secret_value.assert_called_once()


def test_secret_cache_read_error(aws_secret_adaptor):
    """Test handling cache read errors in AWS Lambda"""
    secret_name = "test-secret"
    secret_value = "test-value"

    # Mock AWS Lambda environment
    with patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_NAME": "test-function"}):
        # Mock file operations to raise an error on read
        with patch("builtins.open", side_effect=IOError("Read error")):
            with patch("os.listdir", return_value=[secret_name]):
                aws_secret_adaptor.client.get_secret_value.return_value = {
                    "SecretString": secret_value
                }

                # Should fall back to AWS when cache read fails
                result = aws_secret_adaptor.get_secret(secret_name)
                assert result == secret_value
                aws_secret_adaptor.client.get_secret_value.assert_called_once()
