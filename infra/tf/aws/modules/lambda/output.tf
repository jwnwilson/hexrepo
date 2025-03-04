output lambda_function_invoke_arn {
  value = module.lambda.lambda_function_invoke_arn
}

output lambda_function_name {
  value = module.lambda.lambda_function_name
}

output lambda_role_name {
  value = module.lambda.lambda_role_name
}

output lambda_function_image_tag {
  value = module.lambda.lambda_layer_version
}
