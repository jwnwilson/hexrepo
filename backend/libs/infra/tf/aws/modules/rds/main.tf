# Configure the AWS Provider
provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region     = var.region
}


################################################################################
# RDS Module
################################################################################

# This need to be created outside this module
data "aws_ssm_parameter" "username" {
  name = "/authorizer/${var.environment}/username"
}

# This need to be created outside this module
data "aws_ssm_parameter" "password" {
  name = "/authorizer/${var.environment}/password"
}

module "security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 4"

  name        = "${var.project}-sg-${var.environment}"
  description = "Complete PostgreSQL example security group"
  vpc_id      = var.vpc_id

  # ingress
  ingress_with_cidr_blocks = [
    {
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      description = "PostgreSQL access from within VPC"
      cidr_blocks = var.vpc_cidr_block
    },
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = 5432
      to_port     = 5432
      protocol    = -1
      description = "PostgreSQL access from within VPC"
      cidr_blocks = var.vpc_cidr_block
    },
    {
      from_port   = 0
      to_port     = 0
      protocol    = -1
      description = "Allow all outgoing connections"
      cidr_blocks = "0.0.0.0/0"
    }
  ]
}

module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 3.0"

  identifier = "${var.project}-db-${var.environment}"

  # All available versions: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html#PostgreSQL.Concepts
  engine               = "postgres"
  engine_version       = "11.13"
  family               = "postgres11" # DB parameter group
  major_engine_version = "11"         # DB option group
  instance_class       = "db.t2.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = false

  # NOTE: Do NOT use 'user' as the value for 'username' as it throws:
  # "Error creating DB Instance: InvalidParameterValue: MasterUsername
  # user cannot be used as it is a reserved word used by the engine"
  name                  = "authorizer"
  username              = data.aws_ssm_parameter.username.value
  password              = data.aws_ssm_parameter.password.value
  port                  = 5432

  multi_az               = false
  subnet_ids             = var.vpc_subnet_ids
  vpc_security_group_ids = [module.security_group.security_group_id]

  parameters = [
    {
      name  = "autovacuum"
      value = 1
    },
    {
      name  = "client_encoding"
      value = "utf8"
    }
  ]
}
