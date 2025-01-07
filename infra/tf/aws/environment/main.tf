terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "hexrepo-jwn"
    key    = "hexrepo-env.tfstate"
    dynamodb_table = "terraform-state-lock-dynamo"
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

module "hexrepo_vpc" {
  source = "../modules/vpc"

  environment    = terraform.workspace
  project        = "hexrepo"
  # Cheaper 3rd party alternative to NAT Gateway
  fck_nat_gateway = true
  nat_gateway     = false
  nat_start_time  = "08:00:00"
  nat_stop_time   = "23:00:00"
}

module "bastion_ec2" {
  source = "../modules/bastionhost"

  project                         = "hexrepo"
  vpc_id                          = module.hexrepo_vpc.vpc_id
  subnet_id                       = module.hexrepo_vpc.private_subnet_ids[0]
  instance_type                   = "t2.nano"
  bastion_host_security_group_ids = module.hexrepo_vpc.security_group_ids
  tag_application                 = "bastion"
  start_time                      = "08:00:00"
  stop_time                       = "20:00:00"
}
