.EXPORT_ALL_VARIABLES:

TF_VAR_docker_tag=${docker_tag}
TF_VAR_ecr_api_url={{cookiecutter.AWS_ACCOUNT}}.dkr.ecr.eu-west-1.amazonaws.com/{{cookiecutter.project_slug}}_api
TF_VAR_environment=${environment}
TF_VAR_aws_access_key=${AWS_ACCESS_KEY_ID}
TF_VAR_aws_secret_key=${AWS_SECRET_ACCESS_KEY}
TF_VAR_aws_region=${AWS_DEFAULT_REGION}

init:
	cd tf && terraform init -input=false

plan:
	cd tf && terraform plan -out tfapply

apply:
	cd tf && terraform apply -auto-approve tfapply

destroy:
	cd tf && terraform destroy

init_pipeline:
	cd tf_pipeline && terraform init

apply_pipeline:
	cd tf_pipeline && terraform apply

destroy_pipeline:
	cd tf_pipeline && terraform destroy
