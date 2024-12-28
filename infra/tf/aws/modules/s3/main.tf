module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "${var.project}-${terraform.workspace}-${var.name}"
  acl    = "private"

  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  versioning = {
    enabled = true
  }

  tags = {
    PROJECT     = var.project,
    ENVIRONMENT = terraform.workspace,
    Terraform   = "true"
  }
}