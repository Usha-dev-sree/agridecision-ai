terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ─── VPC & Networking ────────────────────────────────────────────────────────
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "agri-prod-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}

# ─── EKS Cluster (Kubernetes) ────────────────────────────────────────────────
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.15"

  cluster_name    = "agri-prod-eks"
  cluster_version = "1.27"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    general = {
      min_size     = 3
      max_size     = 10
      desired_size = 3
      instance_types = ["t3.medium"]
    }
  }
}

# ─── Amazon RDS (PostgreSQL) ────────────────────────────────────────────────
resource "aws_db_instance" "postgres" {
  allocated_storage    = 50
  max_allocated_storage = 1000
  db_name              = "agridecision_user"
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.medium"
  username             = var.postgres_username
  password             = var.postgres_password
  parameter_group_name = "default.postgres15"
  skip_final_snapshot  = true
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name = aws_db_subnet_group.rds_subnet_group.name
}

# ─── Amazon ElastiCache (Redis) ─────────────────────────────────────────────
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "agri-prod-redis"
  engine               = "redis"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  security_group_ids   = [aws_security_group.redis_sg.id]
  subnet_group_name    = aws_elasticache_subnet_group.redis_subnet_group.name
}

# ─── Managed Kafka (MSK) ─────────────────────────────────────────────────────
resource "aws_msk_cluster" "kafka" {
  cluster_name           = "agri-prod-kafka"
  kafka_version          = "3.2.0"
  number_of_broker_nodes = 3

  broker_node_group_info {
    instance_type = "kafka.t3.small"
    client_subnets = module.vpc.private_subnets
    security_groups = [aws_security_group.kafka_sg.id]
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS_PLAINTEXT"
      in_cluster    = true
    }
  }
}

# ─── Supporting Resources ────────────────────────────────────────────────────
resource "aws_security_group" "db_sg" {
  name   = "rds-postgres-sg"
  vpc_id = module.vpc.vpc_id
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }
}

resource "aws_security_group" "redis_sg" {
  name   = "elasticache-redis-sg"
  vpc_id = module.vpc.vpc_id
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }
}

resource "aws_security_group" "kafka_sg" {
  name   = "msk-kafka-sg"
  vpc_id = module.vpc.vpc_id
  ingress {
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }
}

resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "rds-subnet-group"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_elasticache_subnet_group" "redis_subnet_group" {
  name       = "redis-subnet-group"
  subnet_ids = module.vpc.private_subnets
}
