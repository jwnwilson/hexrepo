output "distribution_id" {
  description = "The ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.s3_distribution.id
}

output "distribution_domain_name" {
  description = "The domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.s3_distribution.domain_name
}

output "distribution_arn" {
  description = "The ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.s3_distribution.arn
}

output "distribution_aliases" {
  description = "The aliases of the CloudFront distribution"
  value       = aws_cloudfront_distribution.s3_distribution.aliases
}

output "origin_access_control_id" {
  description = "The ID of the Origin Access Control"
  value       = aws_cloudfront_origin_access_control.s3_oac.id
}

output "origin_access_control_arn" {
  description = "The ARN of the Origin Access Control"
  value       = aws_cloudfront_origin_access_control.s3_oac.arn
} 