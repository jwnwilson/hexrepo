variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "s3_bucket_id" {
  description = "ID of the S3 bucket"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  type        = string
}

variable "s3_bucket_regional_domain_name" {
  description = "Regional domain name of the S3 bucket"
  type        = string
}

variable "domain_aliases" {
  description = "List of domain aliases for the CloudFront distribution"
  type        = list(string)
  default     = []
}

variable "default_root_object" {
  description = "Default root object for the CloudFront distribution"
  type        = string
  default     = "index.html"
}

variable "enable_spa_routing" {
  description = "Enable SPA routing (serve index.html for 404/403 errors)"
  type        = bool
  default     = true
}

variable "min_ttl" {
  description = "Minimum TTL for cached objects"
  type        = number
  default     = 0
}

variable "default_ttl" {
  description = "Default TTL for cached objects"
  type        = number
  default     = 3600
}

variable "max_ttl" {
  description = "Maximum TTL for cached objects"
  type        = number
  default     = 86400
}

variable "geo_restriction_type" {
  description = "Type of geo restriction"
  type        = string
  default     = "none"
}

variable "geo_restriction_locations" {
  description = "List of locations for geo restriction"
  type        = list(string)
  default     = []
}

variable "use_default_certificate" {
  description = "Use CloudFront default certificate"
  type        = bool
  default     = false
}

variable "acm_certificate_arn" {
  description = "ARN of the ACM certificate"
  type        = string
  default     = null
}

variable "ssl_support_method" {
  description = "SSL support method for the certificate"
  type        = string
  default     = "sni-only"
}

variable "minimum_protocol_version" {
  description = "Minimum protocol version for SSL"
  type        = string
  default     = "TLSv1.2_2021"
}

variable "create_bucket_policy" {
  description = "Whether to create the S3 bucket policy for CloudFront access"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags for the CloudFront distribution"
  type        = map(string)
  default     = {}
} 