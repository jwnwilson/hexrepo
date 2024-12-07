.EXPORT_ALL_VARIABLES:

TF_VAR_docker_tag=${docker_tag}
TF_VAR_environment=${ENVIRONMENT}
TF_VAR_ecr_api_url=${AWS_ACCOUNT}.dkr.ecr.eu-west-1.amazonaws.com/_api
TF_VAR_aws_access_key=${AWS_ACCESS_KEY_ID}
TF_VAR_aws_secret_key=${AWS_SECRET_ACCESS_KEY}
TF_VAR_aws_region=${AWS_DEFAULT_REGION}
TF_STATE_BUCKET=${AWS_TF_STATE_BUCKET}
TF_STATE_REGION=${AWS_DEFAULT_REGION}

tf_shared_init:
	@cd infra/tf/aws/shared  && terraform init -input=false

tf_shared_plan:
	@cd infra/tf/aws/shared  && terraform plan -out tfapply

tf_shared_apply:
	@cd infra/tf/aws/shared  && terraform apply

tf_shared_destroy:
	@cd infra/tf/aws/shared  && terraform destroy

tf_shared_output:
	@cd infra/tf/aws/shared && terraform output -json

tf_workspace:
	@cd infra/tf/aws/environment  && \
	terraform workspace new $(ENVIRONMENT) && \
	terraform workspace select $(ENVIRONMENT) 

tf_env_init:
	@cd infra/tf/aws/environment  && terraform init -input=false

tf_env_plan:
	@cd infra/tf/aws/environment  && terraform plan -out tfapply

tf_env_apply:
	@cd infra/tf/aws/environment  && terraform apply

tf_env_destroy:
	@cd infra/tf/aws/environment  && terraform destroy

tf_env_output:
	@cd infra/tf/aws/environment && terraform output -json