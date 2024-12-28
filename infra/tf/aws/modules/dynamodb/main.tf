module "dynamodb_table" {
  source   = "terraform-aws-modules/dynamodb-table/aws"

  name     = "${var.project}_${var.table_name}_${var.environment}"
  hash_key = "${var.hash_key}"
#   sort_key = "${var.sort_key}"

  attributes = [
    {
      name = "${var.hash_key}"
      type = "${var.hash_key_type}"
    }
    # {
    #   name = "${var.sort_key}"
    #   type = "${var.sort_key_type}"
    # }
  ]

  tags = merge(
    {
        PROJECT     = var.project,
        ENVIRONMENT = var.environment,
        Terraform   = "true"
    },
    var.tags
  )
}