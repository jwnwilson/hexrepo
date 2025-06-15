output dynamodb_table_arn {
  value = module.dynamodb_table.dynamodb_table_arn
}

output table_name {
  value = local.table_name
}
