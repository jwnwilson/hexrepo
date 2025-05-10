
terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "hexrepo-jwn"
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

############
# IAM users
############
module "iam_user1" {
  source = "../../modules/iam-user"

  name = "user1"

  create_iam_user_login_profile = false
  create_iam_access_key         = false
}

module "iam_policy" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name        = "hexrepo-policy"
  path        = "/"
  description = "Permissions to build hexrepo"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "ec2:Describe*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

module "iam_assumable_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"

  trusted_role_arns = [
    "arn:aws:iam::307990089504:root",
    "arn:aws:iam::835367859851:user/anton",
  ]

  create_role = true

  role_name         = "custom"
  role_requires_mfa = true

  custom_role_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonCognitoReadOnly",
    "arn:aws:iam::aws:policy/AlexaForBusinessFullAccess",
  ]
  number_of_custom_role_policy_arns = 2
}