# CS4360 AWS IAM Permissions Plan

Region: us-east-1
Status: Planning only - no AWS roles created

## ECS Task Execution Role

Purpose:
- Allow ECS to download our Docker image from ECR.
- Allow ECS to send container logs to CloudWatch.

Proposed AWS managed policy:
- AmazonECSTaskExecutionRolePolicy

## ECS Application Task Role

Purpose:
- Allow our application to read recorded detection results from S3.
- Allow our application to save and retrieve alerts in DynamoDB.

Proposed permissions:
- s3:GetObject on the detection-results/ prefix
- s3:GetObject on the model-artifacts/ prefix
- dynamodb:PutItem on the cs4360-alerts table
- dynamodb:GetItem on the cs4360-alerts table
- dynamodb:Query on the cs4360-alerts table

## Security Requirements

- Do not store AWS access keys in GitHub.
- Do not embed credentials inside Docker images.
- Keep the S3 bucket private.
- Use separate execution and application task roles.
- Restrict permissions to specific AWS resources.
- Review permissions before creating any IAM roles.

## Current Limitations

- The replay pipeline currently reads local JSON files.
- S3 integration has not been implemented.
- DynamoDB integration has not been implemented.
- AWS deployment has not been performed.
- This document does not create any AWS resources.
