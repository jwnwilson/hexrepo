output "db_password_secret_arn" {
  value = module.db.db_instance_master_user_secret_arn
}

output "db_instance_endpoint" {
  value = module.db.db_instance_endpoint
}

output "db_instance_ro_endpoint" {
  value = module.replica[0].db_instance_endpoint
}


output "db_security_group_id" {
  value = module.security_group.security_group_id
}
