output "aws_lb_http_listener_arn" {
  description = "The ARN of the AWS Load Balancer Listener"
  value       = aws_lb_listener.http.arn
}

output "target_group_arn" {
  description = "The ARN of the target group"
  value       = aws_lb_target_group.lb.arn
}

# output "aws_lb_https_listener_arn" {
#   description = "The ARN of the AWS Load Balancer Listener"
#   value       = aws_lb_listener.https.arn
# }
