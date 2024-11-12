.EXPORT_ALL_VARIABLES:

TF_VAR_docker_tag=${docker_tag}
TF_VAR_environment=${environment}
TF_VAR_ecr_api_url=${AWS_ACCOUNT}.dkr.ecr.eu-west-1.amazonaws.com/_api
TF_VAR_aws_access_key=${AWS_ACCESS_KEY_ID}
TF_VAR_aws_secret_key=${AWS_SECRET_ACCESS_KEY}
TF_VAR_aws_region=${AWS_DEFAULT_REGION}
TF_STATE_BUCKET=${AWS_TF_STATE_BUCKET}
TF_STATE_REGION=${AWS_DEFAULT_REGION}

tf_init:
	cd infra/tf/aws  && terraform init -input=false

tf_plan:
	cd infra/tf/aws  && terraform plan -out tfapply

tf_apply:
	cd infra/tf/aws  && terraform apply -auto-approve tfapply

tf_destroy:
	cd infra/tf/aws  && terraform destroy
