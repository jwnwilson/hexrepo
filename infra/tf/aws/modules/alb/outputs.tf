output "aws_lb_http_listener_arn" {
  description = "The ARN of the AWS Load Balancer Listener"
  value       = var.enabled ? aws_lb_listener.http[0].arn : ""
}

output "target_group_arn" {
  description = "The ARN of the target group"
  value       = var.enabled ? aws_lb_target_group.lb[0].arn : ""
}

# output "aws_lb_https_listener_arn" {
#   description = "The ARN of the AWS Load Balancer Listener"
#   value       = aws_lb_listener.https.arn
# }
