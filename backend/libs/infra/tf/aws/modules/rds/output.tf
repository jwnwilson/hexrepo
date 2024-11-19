output "db_password_secret_name" {
  value = aws_secretsmanager_secret.password.name
}

output "db_instance_endpoint" {
  value = module.db.db_instance_endpoint
}

output "db_security_group_id" {
  value = module.security_group.security_group_id
}