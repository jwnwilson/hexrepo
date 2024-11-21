# Complete using this guide:
# https://medium.com/@ilia.lazebnik/simplifying-aws-private-lambda-gateway-vpc-endpoint-association-with-terraform-b379a247afbf

#   If we attach our lambda to a VPC then we have to use a nat gateway for internet access
#   Do not do this as this is expensive.


module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${var.project}-vpc-${var.environment}"
  cidr = "10.10.0.0/16"

  azs             = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  public_subnets  = ["10.10.1.0/24", "10.10.2.0/24", "10.10.3.0/24"]
  private_subnets = ["10.10.101.0/24", "10.10.102.0/24", "10.10.103.0/24"]

  private_subnet_tags = {
    Tier = "Private"
  }
  public_subnet_tags = {
    Tier = "Public"
  }

  # If we attach our lambda to a VPC then we have to use a nat gateway for internet access
  # Note this costs money
  enable_nat_gateway     = var.nat_gateway
  single_nat_gateway     = var.nat_gateway
  one_nat_gateway_per_az = false

  tags = {
    project     = var.project
    Environment = var.environment
  }
}

# Cheaper 3rd party alternative to NAT Gateway
# data "aws_subnet" "private" {
#   for_each = toset(module.vpc.private_subnets)
#   id       = each.value
# }

# data "aws_subnet" "public" {
#   for_each = toset(module.vpc.public_subnets)
#   id       = each.value
# }

# data "aws_route_table" "private_route_tables" {
#   for_each = toset(module.vpc.private_subnets)
#   subnet_id = each.value
# }

# locals {
  
#   private_subnet_ids_az_map = {
#     for subnet in data.aws_subnet.private :
#     subnet.availability_zone => subnet.id
#   }

#   private_route_table_subnet_map = {
#     for route_table in data.aws_route_table.private_route_tables :
#     route_table.subnet_id => route_table.id
#   }

#   public_subnet_ids_az_map = {
#     for subnet in data.aws_subnet.public :
#     subnet.availability_zone => subnet.id
#   }
# }

# module "fck-nat" {
#   source = "RaJiska/fck-nat/aws"

#   for_each = toset(module.vpc.azs)

#   name          = "${var.project}-nat-${each.key}"
#   vpc_id        = module.vpc.vpc_id
#   subnet_id     = local.public_subnet_ids_az_map[each.key]
#   instance_type = "t4g.nano"

#   update_route_tables = true
#   route_tables_ids = {
#     "private" = local.private_route_table_subnet_map[local.private_subnet_ids_az_map[each.key]]
#   }

#   tags = {
#     Name = "${var.project}-fck-nat-${each.key}"
#   }
# }

module "fck-nat" {
  count = var.fck_nat_gateway ? 1 : 0
  source = "RaJiska/fck-nat/aws"

  name          = "${var.project}-nat"
  vpc_id        = module.vpc.vpc_id
  subnet_id     = "subnet-0831dfb2dea2250b4"
  ha_mode       = false

  update_route_tables = true
  route_tables_ids = {
    "${var.project}-default" = module.vpc.vpc_main_route_table_id
    "${var.project}-private" = "rtb-0ca07f993d6e17bc3"
  }
}
