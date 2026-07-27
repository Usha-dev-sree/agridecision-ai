variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "The target AWS Region for deployment"
}

variable "postgres_username" {
  type        = string
  default     = "postgres"
  description = "Administrator username for RDS PostgreSQL"
}

variable "postgres_password" {
  type        = string
  sensitive   = true
  description = "Administrator password for RDS PostgreSQL"
}
