variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1" # set your preferred region
}

variable "instance_name" {
  description = "Name tag for the EC2 instance"
  type        = string
  default     = "statuspulse-ec2"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.large"
}

variable "disk_size_gb" {
  description = "Root disk size"
  type        = number
  default     = 30
}

variable "allow_ssh_cidr" {
  description = "CIDR allowed to SSH in"
  type        = string
  default     = "0.0.0.0/0" # tighten later
}
