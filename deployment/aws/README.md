
# AWS Deployment Preparation

## CS4360 - Network Anomaly Detection and Automated Threat Analysis

### Purpose

This document outlines the planned AWS deployment process for
the project's containerized backend.

The current backend supports:

- Loading recorded detection results from JSON files.
- Replaying detection results as a simulated stream.
- Creating alerts and adding them to an in-memory queue.
- Running automated tests inside Docker.

The project currently uses recorded data, not live network traffic.

AWS deployment is planned for Weeks 7-8. No AWS resources
have been provisioned as part of this preparation.

## 1. Proposed AWS Architecture

The planned deployment uses:

- Amazon ECR to store the Docker image.
- Amazon ECS with AWS Fargate to execute the container.
- Amazon CloudWatch Logs to collect container output.
- Amazon S3 as a possible storage location for recorded
  detection results and processed artifacts.

Proposed workflow:

    Recorded detection results
        |
        v
    JSON input file
        |
        v
    Docker container running on ECS Fargate
        |
        v
    AlertReplay
        |
        v
    In-memory AlertQueue
        |
        v
    Console output / CloudWatch Logs

Important limitations:

- The alert queue currently exists only in memory.
- Alerts are not persisted after the container exits.
- The replay is not yet connected to the actual detection model.
- Cloud deployment does not provide a production-ready
  investigation pipeline or dashboard.

## 2. Local Docker Image

Build the container from the repository root:

    docker build -t cs4360-anomaly-detection .

Run the automated tests:

    docker run --rm -v "${PWD}/data/processed:/app/data/processed:ro" cs4360-anomaly-detection

The command above is intended for Windows PowerShell.

Run a controlled replay using synthetic test data:

    docker run --rm cs4360-anomaly-detection python -m src.ingestion.run_replay tests/fixtures/detection_results.json --delay 0.5

Expected final output:

    Replay complete. 3 alerts ingested.

The test fixture contains synthetic detection results,
not actual predictions from the project's detection model.

## 3. AWS Prerequisites

Before deployment, the team will need:

1. An AWS account with appropriate permissions.
2. AWS CLI installed and configured.
3. Docker installed.
4. An approved AWS region.
5. An ECR repository.
6. An ECS cluster and Fargate task definition.
7. IAM permissions for ECR, ECS, and CloudWatch Logs.
8. A plan for securely providing input data to the container.

Do not commit AWS access keys, secret keys, or credentials
to the GitHub repository.

## 4. Push the Docker Image to Amazon ECR

The following commands are templates for a future deployment.
Replace the placeholders with the team's actual AWS values.

Set environment variables in PowerShell:

    $AWS_REGION = "<aws-region>"
    $AWS_ACCOUNT_ID = "<aws-account-id>"
    $ECR_REPOSITORY = "cs4360-anomaly-detection"

Create an ECR repository if it does not already exist:

    aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION

Authenticate Docker with ECR:

    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

Build the Docker image:

    docker build -t cs4360-anomaly-detection .

Tag the image:

    docker tag cs4360-anomaly-detection:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY}:latest"

Push the image:

    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY}:latest"

These commands are not required for Week 6 preparation.
Running them later may create AWS resources and charges.

## 5. ECS Fargate Task Preparation

The team will need to define:

- Container image URI from ECR.
- CPU and memory allocation.
- Task execution IAM role.
- CloudWatch Logs configuration.
- Network configuration and security groups.
- Container command and input data location.

The current Dockerfile runs pytest by default.

For a replay task, override the container command with:

    python -m src.ingestion.run_replay tests/fixtures/detection_results.json --delay 0.5

This command uses synthetic test data bundled into the image.
It is intended only for initial deployment verification.

Production or integration data must be provided separately.

Because the replay command completes after processing its input,
it is better suited to an ECS task than a continuously running
ECS service at this stage.

## 6. Data and Storage Considerations

The existing container image does not include the full
NSL-KDD or CICIDS2017 datasets.

Large processed datasets are excluded from the Docker image.

For future AWS integration, the team must decide how
to provide input data and persist generated alerts.

Possible approaches include:

- Amazon S3 for recorded input files.
- Amazon S3 for processed artifacts.
- A persistent database or message queue for alerts.

These are proposed options, not implemented components.

The current replay command reads a local JSON file.
It does not directly download files from S3.

## 7. Verification Plan

After deployment, verify that:

1. The ECS task starts successfully.
2. The container can access its input file.
3. The replay command executes without errors.
4. Three synthetic test alerts are created.
5. The output appears in CloudWatch Logs.
6. The task exits successfully.
7. No AWS credentials are exposed in logs or source code.

For larger integration tests, use actual detection results
once the model interface is available.

## 8. Week 6 Completion Status

Completed:

- Docker containerization.
- Simulated alert streaming.
- Replay command-line interface.
- Synthetic detection-result fixture.
- Automated CLI tests.
- 102 automated tests passing locally.
- 102 automated tests passing inside Docker.
- Successful local and Docker replay demonstrations.
- AWS deployment planning documentation.

Not yet completed:

- AWS account configuration and resource provisioning.
- ECR image upload.
- ECS Fargate task deployment.
- CloudWatch integration verification.
- Persistent alert storage.
- Integration with the final anomaly-detection model.

These remaining implementation tasks will be addressed
during later integration and deployment work.
