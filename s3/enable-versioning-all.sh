#!/bin/bash

# List of S3 buckets
buckets=$(aws s3api list-buckets --query "Buckets[].Name" --output text)

for bucket in $buckets; do
  echo "Checking versioning status for $bucket..."

  status=$(aws s3api get-bucket-versioning --bucket $bucket --query "Status" --output text)

  if [ "$status" == "Enabled" ]; then
    echo "Versioning is already enabled for $bucket."
  else
    echo "Enabling versioning for $bucket..."
    aws s3api put-bucket-versioning --bucket $bucket --versioning-configuration Status=Enabled
    echo "Versioning enabled for $bucket."
  fi
done

echo "Versioning setup completed."