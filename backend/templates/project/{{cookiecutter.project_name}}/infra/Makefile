.EXPORT_ALL_VARIABLES:

TF_VAR_docker_tag=${docker_tag}
TF_VAR_environment=${environment}
{ % if cookiecutter.cloud_provider == 'aws' %}
TF_VAR_ecr_api_url=123456.dkr.ecr.eu-west-1.amazonaws.com/{{cookiecutter.project_slug}}_api
TF_VAR_aws_access_key=${AWS_ACCESS_KEY_ID}
TF_VAR_aws_secret_key=${AWS_SECRET_ACCESS_KEY}
TF_VAR_aws_region=${AWS_DEFAULT_REGION}
{ % endif %}

init:
	cd tf/{{cookiecutter.cloud_provider}}  && terraform init -input=false

plan:
	cd tf/{{cookiecutter.cloud_provider}}  && terraform plan -out tfapply

apply:
	cd tf/{{cookiecutter.cloud_provider}}  && terraform apply -auto-approve tfapply

destroy:
	cd tf/{{cookiecutter.cloud_provider}}  && terraform destroy
