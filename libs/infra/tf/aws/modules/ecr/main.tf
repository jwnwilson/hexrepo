terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

variable "project" {}
resource "aws_ecr_repository" "ecr_repo" {
  name                 = var.project
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}
