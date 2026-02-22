# Deployment Guide

Complete guide for deploying APIverse to AWS.

## Prerequisites

### Required Tools

- **AWS CLI** - Configured with credentials
- **Node.js** 18+ - For AWS CDK
- **Python** 3.12+ - For Lambda functions
- **Docker** - For building Lambda images
- **Git** - For version control

### AWS Account Setup

1. **Create AWS Account** (if you don't have one)
2. **Configure AWS CLI**:
```bash
aws configure
```
Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `eu-west-1`)
- Default output format (`json`)

3. **Verify credentials**:
```bash
aws sts get-caller-identity
```

---

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/apiverse.git
cd apiverse
```

### 2. Install CDK Dependencies

```bash
cd infra/cdk
npm install
```

### 3. Bootstrap CDK (First Time Only)

This creates the necessary S3 buckets and IAM roles for CDK:

```bash
cdk bootstrap aws://ACCOUNT-ID/REGION
```

Example:
```bash
cdk bootstrap aws://123456789012/eu-west-1
```

---

## Deployment

### Deploy Infrastructure

From the `infra/cdk` directory:

```bash
cdk deploy
```

This will:
1. Create VPC with public and private subnets
2. Deploy RDS PostgreSQL database
3. Deploy ElastiCache Redis cluster
4. Build and deploy Lambda function (Docker image)
5. Create API Gateway
6. Set up EventBridge and SQS for webhooks
7. Create Secrets Manager secret for database credentials

**Deployment time**: ~15-20 minutes (RDS takes the longest)

### Deployment Output

After successful deployment, you'll see outputs like:

```
Outputs:
ApiVerseStack.ApiEndpoint = https://abc123.execute-api.eu-west-1.amazonaws.com/dev
ApiVerseStack.RDSEndpoint = apiverse-db.abc123.eu-west-1.rds.amazonaws.com
ApiVerseStack.RedisEndpoint = apiverse-redis.abc123.cache.amazonaws.com
ApiVerseStack.SecretArn = arn:aws:secretsmanager:eu-west-1:123456789012:secret:RDSSecret-abc123
```

**Save these values!** You'll need them for testing and configuration.

---

## Database Migration

After deployment, you need to manually run the migration Lambda to set up the database schema.

**Using AWS Console:**
1. Go to AWS Lambda Console
2. Find `apiverse-migrate` function
3. Click "Test" with an empty event `{}`
4. Check logs in CloudWatch

**Using AWS CLI:**
```bash
aws lambda invoke \
  --function-name apiverse-migrate \
  --payload '{}' \
  response.json

cat response.json
```

The migration Lambda will:
- Connect to RDS using credentials from Secrets Manager
- Run all pending Alembic migrations
- Create all necessary tables and indexes

---

## Verification

### 1. Test Health Endpoint

```bash
curl https://your-api-gateway-url/dev/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "apiverse",
  "version": "0.1.0"
}
```

### 2. Test Registration

```bash
curl -X POST https://your-api-gateway-url/dev/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'
```

### 3. Check CloudWatch Logs

1. Go to CloudWatch Console
2. Navigate to Log Groups
3. Find `/aws/lambda/apiverse-api`
4. Check recent logs for errors

---

## Configuration

### Environment Variables

The Lambda function has these environment variables (set by CDK):

- `RDS_SECRET_ARN` - Secrets Manager ARN for database credentials
- `RDS_ENDPOINT` - RDS endpoint
- `RDS_PORT` - Database port (5432)
- `DATABASE_NAME` - Database name (apiverse)
- `REDIS_HOST` - Redis endpoint
- `REDIS_PORT` - Redis port (6379)
- `JWT_SECRET_KEY` - JWT signing key
- `JWT_ALGORITHM` - JWT algorithm (HS256)
- `APP_NAME` - Application name
- `DEBUG` - Debug mode (false)

### Update Environment Variables

To update environment variables:

1. Edit `infra/cdk/lib/constructs/lambda.ts`
2. Modify the `environment` section
3. Redeploy:
```bash
cdk deploy
```

---

## Updating the Application

### Code Changes

1. **Make changes** to Python code in `services/api/`
2. **Commit changes**:
```bash
git add .
git commit -m "Your changes"
git push
```
3. **Redeploy**:
```bash
cd infra/cdk
cdk deploy
```

CDK will:
- Rebuild the Docker image
- Push to ECR
- Update Lambda function

### Database Schema Changes

1. **Create migration**:
```bash
cd services/api
alembic revision --autogenerate -m "Description of changes"
```

2. **Review migration** in `alembic/versions/`

3. **Test locally**:
```bash
alembic upgrade head
```

4. **Commit and deploy**:
```bash
git add .
git commit -m "Add migration"
git push
cd ../../infra/cdk
cdk deploy
```

5. **Run migration Lambda** manually (see Database Migration section above)

---

## Monitoring

### CloudWatch Logs

**API Logs**:
- Log Group: `/aws/lambda/apiverse-api`
- Contains all application logs
- Retention: 7 days

**Migration Logs**:
- Log Group: `/aws/lambda/apiverse-migrate`
- Contains migration execution logs

### CloudWatch Metrics

Monitor these Lambda metrics:
- Invocations
- Duration
- Errors
- Throttles
- Concurrent Executions

### Database Monitoring

**RDS Metrics**:
- CPU Utilization
- Database Connections
- Free Storage Space
- Read/Write IOPS

**Redis Metrics**:
- CPU Utilization
- Cache Hits/Misses
- Evictions
- Network Bytes In/Out

---

## Troubleshooting

### Lambda Timeout

**Symptom**: 504 Gateway Timeout

**Solutions**:
1. Increase Lambda timeout in `lambda.ts`:
```typescript
timeout: cdk.Duration.seconds(60)
```
2. Optimize database queries
3. Add connection pooling

### Database Connection Issues

**Symptom**: "Could not connect to database"

**Solutions**:
1. Check security groups allow Lambda → RDS
2. Verify RDS is in private subnet
3. Check Secrets Manager credentials
4. Verify VPC configuration

### Migration Failures

**Symptom**: Migration Lambda fails

**Solutions**:
1. Check CloudWatch logs for specific error
2. Verify database credentials in Secrets Manager
3. Test migration locally first
4. Check if migration already applied

---

## Rollback

### Rollback Deployment

If deployment fails or causes issues:

```bash
# View stack history
aws cloudformation describe-stack-events \
  --stack-name ApiVerseStack

# Rollback to previous version
aws cloudformation rollback-stack \
  --stack-name ApiVerseStack
```

### Rollback Database Migration

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>
```

---

## Cleanup

### Delete All Resources

**Warning**: This will delete all data!

```bash
cd infra/cdk
cdk destroy
```

This removes:
- Lambda functions
- API Gateway
- RDS database (and all data)
- ElastiCache cluster
- VPC and networking
- Secrets Manager secrets

### Partial Cleanup

To keep some resources:

1. Edit `apiverse-stack.ts`
2. Comment out resources to keep
3. Run `cdk deploy`

---

## Support

For deployment issues:
- Check CloudWatch Logs first
- Review AWS CloudFormation events
- Open an issue on GitHub with logs
- Check AWS Service Health Dashboard

