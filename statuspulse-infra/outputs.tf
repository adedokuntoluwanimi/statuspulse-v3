output "instance_public_ip" {
  value = aws_instance.this.public_ip
}

output "ssh_private_key_path" {
  value     = local_file.private_key_pem.filename
  sensitive = true
}

output "ssh_command" {
  value = "ssh -i ${local_file.private_key_pem.filename} ubuntu@${aws_instance.this.public_ip}"
}
