output "zone_id" {
  description = "The ID of the Route53 hosted zone"
  value       = aws_route53_zone.hexrepo.zone_id
}

output "zone_name" {
  description = "The name of the Route53 hosted zone"
  value       = aws_route53_zone.hexrepo.name
}

output "name_servers" {
  description = "The name servers for the Route53 hosted zone"
  value       = aws_route53_zone.hexrepo.name_servers
} 