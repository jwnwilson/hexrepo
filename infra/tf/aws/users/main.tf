terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key = "{{cookiecutter.project_slug}}-users.tfstate"
  }
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region  = var.aws_region
}

module "iam_user1" {
  source = "terraform-aws-modules/iam/aws/modules/iam-user"

  name = "monorepo"

  create_iam_user_login_profile = false
  create_iam_access_key         = true
}

#####################################################################################
# IAM group for users with custom access
#####################################################################################
module "iam_group_with_monorepo_policies" {
  source = "terraform-aws-modules/iam/aws/modules/iam-group-with-policies"

  name = "monorepo"
  path = "/monorepo/"

  group_users = [
    module.iam_user1.iam_user_name,
  ]

  custom_group_policy_arns = [
  ]

  custom_group_policies = [
    {
      name   = "AllowMonorepoWrite"
      policy = data.aws_iam_policy_document.monorepo.json
    },
  ]
}

######################
# IAM policy
######################
data "aws_iam_policy_document" "monorepo" {
  statement {
    actions = [
      "s3:ListBuckets",
    ]

    resources = ["*"]
  }
}