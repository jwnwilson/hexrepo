module "dynamodb_table" {
  source   = "terraform-aws-modules/dynamodb-table/aws"

  name     = "${var.project}_${var.environment}"
  hash_key = "${var.hash_key}"

  attributes = [
    {
      name = "${var.hash_key}"
      type = "${var.hash_key_type}"
    }
  ]

  tags = merge(
    {
        ENVIRONMENT = var.environment,
        Terraform   = "true"
    },
    var.tags
  )
}