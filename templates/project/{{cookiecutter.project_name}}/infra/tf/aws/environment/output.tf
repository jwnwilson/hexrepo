
# output "db_migrator_lambda_name" {
#   value = module.migrate_db_task.lambda_function_name
# }

{% if cookiecutter.use_db == "y" %}
output "db_secret_name" {
  value = data.aws_secretsmanager_secret.db_secret.name
}

output "db_url" {
  value = local.db_url
}
{% endif %}