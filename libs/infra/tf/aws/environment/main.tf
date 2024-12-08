terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key    = "monorepo-env.tfstate"
  }
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "monorepo_vpc" {
  source = "../modules/vpc"

  environment    = terraform.workspace
  project        = "monorepo"
  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
  aws_region     = var.aws_region
  # Cheaper 3rd party alternative to NAT Gateway
  fck_nat_gateway = true
  nat_gateway     = false
  nat_start_time  = "08:00:00"
  nat_stop_time   = "23:00:00"
}

module "bastion_ec2" {
  source = "../modules/bastionhost"

  project                         = "monorepo"
  vpc_id                          = module.monorepo_vpc.vpc_id
  subnet_id                       = module.monorepo_vpc.private_subnet_ids[0]
  instance_type                   = "t2.nano"
  bastion_host_security_group_ids = module.monorepo_vpc.security_group_ids
  tag_application                 = "bastion"
  start_time                      = "08:00:00"
  stop_time                       = "20:00:00"
}
