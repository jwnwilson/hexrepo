output "vpc_cidr_block" {
  value = module.vpc.vpc_cidr_block
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "vpc_subnet_ids" {
  value = module.vpc.vpc_subnet_ids
}

output "vpc_private_subnet_ids" {
  value = module.vpc.vpc_private_subnet_ids
}
