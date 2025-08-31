output "bucket_name" {
  value = module.s3_bucket.s3_bucket_bucket_domain_name
}

output "bucket_id" {
  value = module.s3_bucket.s3_bucket_id
}

output "arn" {
  value = module.s3_bucket.s3_bucket_arn
}

output "bucket_regional_domain_name" {
  value = module.s3_bucket.s3_bucket_bucket_regional_domain_name
}