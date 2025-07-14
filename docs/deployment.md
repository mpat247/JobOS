# Deployment Guide

## Overview

JobOS is deployed using containerized services on AWS infrastructure. This guide covers both staging and production deployments.

## Prerequisites

Before deploying JobOS, ensure you have:

- AWS CLI configured with appropriate permissions
- Docker installed locally
- GitHub repository with Actions enabled
- Supabase project configured
- Domain name and SSL certificates (for production)

## Infrastructure Setup

### AWS Services Required

1. **Elastic Container Registry (ECR)** - Container image storage
2. **App Runner** - Serverless container deployment
3. **Route 53** - DNS management
4. **CloudFront** - CDN for static assets
5. **Systems Manager Parameter Store** - Secret management

### 1. ECR Repository Creation

```bash
# Create repositories for both services
aws ecr create-repository --repository-name jobos-frontend --region us-east-1
aws ecr create-repository --repository-name jobos-scraper --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### 2. Parameter Store Configuration

Store sensitive configuration in AWS Systems Manager:

```bash
# Supabase configuration
aws ssm put-parameter --name "/jobos/supabase/url" --value "your-supabase-url" --type "SecureString"
aws ssm put-parameter --name "/jobos/supabase/anon-key" --value "your-anon-key" --type "SecureString"
aws ssm put-parameter --name "/jobos/supabase/service-key" --value "your-service-key" --type "SecureString"

# Database configuration
aws ssm put-parameter --name "/jobos/database/url" --value "your-database-url" --type "SecureString"

# Redis configuration
aws ssm put-parameter --name "/jobos/redis/url" --value "your-redis-url" --type "SecureString"

# Django secret key
aws ssm put-parameter --name "/jobos/django/secret-key" --value "your-secret-key" --type "SecureString"
```

## GitHub Actions CI/CD

### Repository Secrets

Configure the following secrets in your GitHub repository:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ACCOUNT_ID`
- `AWS_REGION`

### Workflow Configuration

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy JobOS

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "18"
          cache: "npm"
          cache-dependency-path: app/package-lock.json

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install frontend dependencies
        run: |
          cd app
          npm ci

      - name: Install backend dependencies
        run: |
          cd scraper
          pip install -r requirements.txt

      - name: Run frontend tests
        run: |
          cd app
          npm run test:ci

      - name: Run backend tests
        run: |
          cd scraper
          python manage.py test

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/staging'

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Set environment suffix
        id: env
        run: |
          if [[ $GITHUB_REF == 'refs/heads/main' ]]; then
            echo "suffix=prod" >> $GITHUB_OUTPUT
          else
            echo "suffix=staging" >> $GITHUB_OUTPUT
          fi

      - name: Build and push frontend image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: jobos-frontend
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd app
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest-${{ steps.env.outputs.suffix }}
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest-${{ steps.env.outputs.suffix }}

      - name: Build and push scraper image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: jobos-scraper
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd scraper
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest-${{ steps.env.outputs.suffix }}
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest-${{ steps.env.outputs.suffix }}

      - name: Deploy to App Runner
        run: |
          # Update App Runner services with new images
          aws apprunner start-deployment --service-arn ${{ secrets.FRONTEND_SERVICE_ARN }}
          aws apprunner start-deployment --service-arn ${{ secrets.SCRAPER_SERVICE_ARN }}
```

## App Runner Configuration

### Frontend Service (apprunner-frontend.yaml)

```yaml
version: 1.0
runtime: docker
build:
  commands:
    build:
      - echo "Build completed"
run:
  runtime-version: latest
  command: npm start
  network:
    port: 3000
    env: PORT
  env:
    - name: NODE_ENV
      value: production
    - name: NEXT_PUBLIC_SUPABASE_URL
      value: "{{resolve:ssm:/jobos/supabase/url}}"
    - name: NEXT_PUBLIC_SUPABASE_ANON_KEY
      value: "{{resolve:ssm:/jobos/supabase/anon-key}}"
```

### Backend Service (apprunner-scraper.yaml)

```yaml
version: 1.0
runtime: docker
build:
  commands:
    build:
      - echo "Build completed"
run:
  runtime-version: latest
  command: |
    python manage.py migrate &&
    gunicorn scraperproject.wsgi:application --bind 0.0.0.0:8000 --workers 3
  network:
    port: 8000
    env: PORT
  env:
    - name: DEBUG
      value: "False"
    - name: DATABASE_URL
      value: "{{resolve:ssm:/jobos/database/url}}"
    - name: REDIS_URL
      value: "{{resolve:ssm:/jobos/redis/url}}"
    - name: SECRET_KEY
      value: "{{resolve:ssm:/jobos/django/secret-key}}"
```

## Production Deployment

### 1. Domain Configuration

#### Route 53 Setup

```bash
# Create hosted zone
aws route53 create-hosted-zone --name jobos.com --caller-reference $(date +%s)

# Create CNAME records for App Runner
aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch file://route53-changes.json
```

#### CloudFront Distribution

```json
{
  "CallerReference": "jobos-cloudfront-2024",
  "Comment": "JobOS CloudFront Distribution",
  "DefaultCacheBehavior": {
    "TargetOriginId": "jobos-frontend",
    "ViewerProtocolPolicy": "redirect-to-https",
    "Compress": true,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    }
  },
  "Origins": [
    {
      "Id": "jobos-frontend",
      "DomainName": "your-app-runner-url.com",
      "CustomOriginConfig": {
        "HTTPPort": 443,
        "OriginProtocolPolicy": "https-only"
      }
    }
  ],
  "Enabled": true,
  "PriceClass": "PriceClass_100"
}
```

### 2. SSL Certificate

```bash
# Request certificate via ACM
aws acm request-certificate \
  --domain-name jobos.com \
  --subject-alternative-names www.jobos.com \
  --validation-method DNS \
  --region us-east-1
```

### 3. Environment-Specific Configurations

#### Production Environment Variables

```bash
# Production-specific parameters
aws ssm put-parameter --name "/jobos/prod/database/url" --value "production-db-url" --type "SecureString"
aws ssm put-parameter --name "/jobos/prod/redis/url" --value "production-redis-url" --type "SecureString"
```

#### Staging Environment Variables

```bash
# Staging-specific parameters
aws ssm put-parameter --name "/jobos/staging/database/url" --value "staging-db-url" --type "SecureString"
aws ssm put-parameter --name "/jobos/staging/redis/url" --value "staging-redis-url" --type "SecureString"
```

## Monitoring and Logging

### CloudWatch Configuration

#### Log Groups

```bash
# Create log groups
aws logs create-log-group --log-group-name /aws/apprunner/jobos-frontend/application
aws logs create-log-group --log-group-name /aws/apprunner/jobos-scraper/application
```

#### Metrics and Alarms

```bash
# Create CPU utilization alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "JobOS-Frontend-HighCPU" \
  --alarm-description "High CPU utilization for JobOS frontend" \
  --metric-name CPUUtilization \
  --namespace AWS/AppRunner \
  --statistic Average \
  --period 300 \
  --threshold 80.0 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

### Application Performance Monitoring

#### Frontend Monitoring

```typescript
// Add to app/src/lib/monitoring.ts
import { Analytics } from "@vercel/analytics/react";

export function initMonitoring() {
  // Initialize error tracking
  if (process.env.NODE_ENV === "production") {
    // Configure error reporting
  }
}
```

#### Backend Monitoring

```python
# Add to scraper/monitoring.py
import logging
import boto3

def setup_cloudwatch_logging():
    cloudwatch = boto3.client('logs')
    handler = CloudWatchLogsHandler(
        log_group='/aws/apprunner/jobos-scraper/application'
    )
    logging.getLogger().addHandler(handler)
```

## Backup and Recovery

### Database Backups

```bash
# Automated Supabase backups are handled by Supabase
# Additional backup strategy for critical data
aws s3 sync s3://jobos-backups/database/ ./backups/
```

### Application State Recovery

```bash
# Redis backup
redis-cli --rdb backup.rdb

# Upload to S3
aws s3 cp backup.rdb s3://jobos-backups/redis/$(date +%Y%m%d)/
```

## Health Checks and Monitoring

### Health Check Endpoints

#### Frontend Health Check

```typescript
// app/src/pages/api/health.ts
export default function handler(req, res) {
  res.status(200).json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version,
  });
}
```

#### Backend Health Check

```python
# scraper/health/views.py
from django.http import JsonResponse
from django.views import View

class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': self.check_database(),
            'redis': self.check_redis(),
        })
```

## Scaling Configuration

### Auto Scaling

App Runner automatically scales based on traffic, but you can configure:

```yaml
# apprunner.yaml scaling configuration
auto_scaling_configuration:
  max_concurrency: 100
  max_size: 10
  min_size: 1
```

### Performance Optimization

#### Frontend Optimizations

```dockerfile
# Multi-stage build for production
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

#### Backend Optimizations

```dockerfile
# Production-optimized Django container
FROM python:3.11-slim AS production
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "scraperproject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

## Security Considerations

### Environment Security

1. **Secret Management**: Use AWS Parameter Store for all secrets
2. **Network Security**: Configure VPC and security groups appropriately
3. **Access Control**: Implement least privilege IAM policies
4. **SSL/TLS**: Enforce HTTPS for all communications
5. **Input Validation**: Sanitize all user inputs
6. **Rate Limiting**: Implement API rate limiting

### Production Checklist

- [ ] All secrets stored in Parameter Store
- [ ] SSL certificates configured
- [ ] CloudFront distribution set up
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented
- [ ] Security groups properly configured
- [ ] Health checks operational
- [ ] Auto-scaling configured
- [ ] Error tracking enabled
- [ ] Performance monitoring active

This deployment guide ensures a robust, scalable, and secure production environment for JobOS.
