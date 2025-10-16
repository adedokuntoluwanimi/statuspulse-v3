############################################
# AWS Provider
############################################
provider "aws" {
  region = "us-east-1"
}

############################################
# AMI: Latest Ubuntu 22.04 LTS for region
############################################
data "aws_ami" "ubuntu_2204" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

############################################
# Key pair (Terraform generates SSH key)
############################################
resource "tls_private_key" "ssh" {
  algorithm = "ED25519"
}

resource "aws_key_pair" "this" {
  key_name   = "${var.instance_name}-key"
  public_key = tls_private_key.ssh.public_key_openssh
}

# Save private key to local file with correct permissions
resource "local_file" "private_key_pem" {
  filename        = "${path.module}/${var.instance_name}.pem"
  content         = tls_private_key.ssh.private_key_pem
  file_permission = "0400"
}

############################################
# Security group
############################################
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "this" {
  name        = "${var.instance_name}-sg"
  description = "Security group for StatusPulse EC2"
  vpc_id      = data.aws_vpc.default.id

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allow_ssh_cidr]
  }

  # Frontend (Next.js)
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Backend (FastAPI)
  ingress {
    from_port   = 8081
    to_port     = 8081
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Jenkins (optional)
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.instance_name}-sg"
  }
}

############################################
# User data: install Docker + Docker Compose
############################################
locals {
  user_data = <<-EOT
    #!/bin/bash
    set -eux

    apt-get update -y
    apt-get install -y ca-certificates curl gnupg lsb-release

    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    systemctl enable docker
    systemctl start docker

    mkdir -p /opt/statuspulse/data
    chown ubuntu:ubuntu /opt/statuspulse -R || true

    if command -v ufw >/dev/null 2>&1; then
      ufw allow 22/tcp || true
      ufw allow 80/tcp || true
      ufw allow 3000/tcp || true
      ufw allow 8081/tcp || true
      ufw allow 8080/tcp || true
    fi
  EOT
}

############################################
# EC2 instance
############################################
resource "aws_instance" "this" {
  ami                         = data.aws_ami.ubuntu_2204.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.this.key_name
  vpc_security_group_ids      = [aws_security_group.this.id]
  subnet_id                   = data.aws_subnets.default.ids[0]
  associate_public_ip_address = true
  user_data                   = local.user_data

  root_block_device {
    volume_size           = var.disk_size_gb
    volume_type           = "gp3"
    delete_on_termination = false # keeps EBS volume even if destroyed
    encrypted             = true
  }

  tags = {
    Name = var.instance_name
  }
}

############################################
# Outputs
############################################
output "instance_public_ip" {
  value = aws_instance.this.public_ip
}

output "ssh_command" {
  value = "ssh -i ./${var.instance_name}.pem ubuntu@${aws_instance.this.public_ip}"
}

output "ssh_private_key_path" {
  value     = local_file.private_key_pem.filename
  sensitive = true
}

