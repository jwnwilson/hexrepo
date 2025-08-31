# CloudFront Origin Access Control
resource "aws_cloudfront_origin_access_control" "s3_oac" {
  name                              = "${var.project}-s3-oac"
  description                       = "Origin Access Control for S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name              = var.s3_bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.s3_oac.id
    origin_id                = "S3-${var.s3_bucket_name}"
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = var.default_root_object
  aliases             = var.domain_aliases

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${var.s3_bucket_name}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = var.min_ttl
    default_ttl            = var.default_ttl
    max_ttl                = var.max_ttl
  }

  # Handle SPA routing - serve index.html for 404s
  dynamic "custom_error_response" {
    for_each = var.enable_spa_routing ? [1] : []
    content {
      error_code         = 404
      response_code      = "200"
      response_page_path = "/${var.default_root_object}"
    }
  }

  # Handle SPA routing - serve index.html for 403s
  dynamic "custom_error_response" {
    for_each = var.enable_spa_routing ? [1] : []
    content {
      error_code         = 403
      response_code      = "200"
      response_page_path = "/${var.default_root_object}"
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = var.geo_restriction_type
      locations        = var.geo_restriction_locations
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = var.use_default_certificate
    acm_certificate_arn           = var.acm_certificate_arn
    ssl_support_method            = var.ssl_support_method
    minimum_protocol_version      = var.minimum_protocol_version
  }

  tags = merge(var.tags, {
    PROJECT     = var.project
    ENVIRONMENT = var.environment
    Terraform   = "true"
  })
}

# S3 bucket policy to allow CloudFront access
resource "aws_s3_bucket_policy" "cloudfront_access" {
  count  = var.create_bucket_policy ? 1 : 0
  bucket = var.s3_bucket_id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontServicePrincipal"
        Effect    = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${var.s3_bucket_arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.s3_distribution.arn
          }
        }
      }
    ]
  })
} 