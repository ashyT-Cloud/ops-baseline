#!/bin/bash
set -euxo pipefail
apt-get update -y
apt-get install -y git awscli
curl -fsSL https://get.docker.com | sh
usermod -aG docker ubuntu
systemctl enable --now docker
