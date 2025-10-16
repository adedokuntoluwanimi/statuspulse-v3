variable "instance_name" {
  default = "statuspulse-ec2"
}

variable "instance_type" {
  default = "t2.large"
}

variable "disk_size_gb" {
  default = 30
}

variable "allow_ssh_cidr" {
  description = "Allowed SSH source"
  default     = "0.0.0.0/0"
}

