variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  type    = string
  default = "t3.small"
}

variable "allowed_cidrs" {
  description = "IPs allowed to SSH and open Grafana, eg. [\"1.2.3.4/32\"]"
  type        = list(string)
}

variable "alert_email" {
  type = string
}

variable "ssh_public_key_path" {
  type    = string
  default = "~/.ssh/ops-baseline.pub"
}
