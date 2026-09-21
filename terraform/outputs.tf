output "public_ip" {
  value = aws_eip.app.public_ip
}

output "backup_bucket" {
  value = aws_s3_bucket.backups.bucket
}

output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}
