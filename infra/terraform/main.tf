terraform {
  required_version = ">= 1.9"

  backend "s3" {
    bucket = "upl-terraform-state"
    key    = "upl/terraform.tfstate"
    region = "us-east-1"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# VPC
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${local.name_prefix}-vpc"
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway   = true
  single_nat_gateway   = var.environment != "prod"
  enable_dns_hostnames = true

  tags = var.tags
}

# EKS Cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${local.name_prefix}-cluster"
  cluster_version = "1.30"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access = var.environment != "prod"

  eks_managed_node_groups = {
    system = {
      name         = "${local.name_prefix}-system"
      instance_types = ["t3.medium"]
      min_size     = 1
      max_size     = 3
      desired_size = 1
      subnet_ids   = module.vpc.private_subnets
      labels = { "node-group" = "system" }
    }
    ke = {
      name         = "${local.name_prefix}-ke"
      instance_types = ["t3.large"]
      min_size     = 1
      max_size     = 5
      desired_size = 2
      subnet_ids   = module.vpc.private_subnets
      labels = { "node-group" = "ke" }
    }
    pipeline = {
      name         = "${local.name_prefix}-pipeline"
      instance_types = ["t3.large"]
      min_size     = 1
      max_size     = 5
      desired_size = 2
      subnet_ids   = module.vpc.private_subnets
      labels = { "node-group" = "pipeline" }
    }
  }

  tags = var.tags
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier = "${local.name_prefix}-postgres"
  engine     = "postgres"
  engine_version = "16.3"

  instance_class    = var.environment == "prod" ? "db.r6g.large" : "db.t3.medium"
  allocated_storage = var.environment == "prod" ? 100 : 20
  storage_type      = "gp3"

  db_name  = "openquery"
  username = var.rds_username
  password = random_password.rds_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.rds.name

  backup_retention_period = var.environment == "prod" ? 30 : 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = var.environment != "prod"
  deletion_protection = var.environment == "prod"

  tags = var.tags
}

resource "random_password" "rds_password" {
  length  = 24
  special = false
}

resource "aws_db_subnet_group" "rds" {
  name       = "${local.name_prefix}-rds-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "rds" {
  name_prefix = "${local.name_prefix}-rds-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${local.name_prefix}-redis"
  engine               = "redis"
  engine_version       = "7.1"
  node_type            = var.environment == "prod" ? "cache.r6g.large" : "cache.t3.micro"
  num_cache_nodes      = var.environment == "prod" ? 2 : 1
  parameter_group_name = "default.redis7"

  subnet_group_name = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]

  tags = var.tags
}

resource "aws_elasticache_subnet_group" "redis" {
  name       = "${local.name_prefix}-redis-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "redis" {
  name_prefix = "${local.name_prefix}-redis-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${local.name_prefix}-alb"
  internal           = var.environment == "prod"
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = module.vpc.public_subnets

  tags = var.tags
}

resource "aws_lb_target_group" "backend" {
  name     = "${local.name_prefix}-backend"
  port     = 8100
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id
  health_check {
    path = "/api/v1/health/live"
    port = 8100
  }
}

resource "aws_lb_target_group" "frontend" {
  name     = "${local.name_prefix}-frontend"
  port     = 3000
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id
  health_check {
    path = "/api/v1/health/live"
    port = 3000
  }
}

resource "aws_lb_listener" "main" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      status_code  = "404"
    }
  }
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.main.arn
  priority     = 100
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}

resource "aws_lb_listener_rule" "frontend" {
  listener_arn = aws_lb_listener.main.arn
  priority     = 200
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
  condition {
    path_pattern {
      values = ["/*"]
    }
  }
}

resource "aws_security_group" "alb" {
  name_prefix = "${local.name_prefix}-alb-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Qdrant on EC2 (or use Qdrant Cloud)
resource "aws_instance" "qdrant" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.large"
  subnet_id     = module.vpc.private_subnets[0]

  vpc_security_group_ids = [aws_security_group.qdrant.id]

  user_data = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io
    docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
      -v /opt/qdrant:/qdrant/storage \
      qdrant/qdrant:latest
  EOF

  tags = merge(var.tags, { Name = "${local.name_prefix}-qdrant" })
}

data "aws_ami" "ubuntu" {
  most_recent = true
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
  owners = ["099720109477"]
}

resource "aws_security_group" "qdrant" {
  name_prefix = "${local.name_prefix}-qdrant-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6333
    to_port         = 6334
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }
}

# Route53 DNS
data "aws_route53_zone" "main" {
  name         = var.domain_name
  private_zone = false
}

resource "aws_route53_record" "app" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = var.environment == "prod" ? "app.${var.domain_name}" : "${var.environment}.app.${var.domain_name}"
  type    = "A"
  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}
