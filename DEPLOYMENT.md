# Deployment Guide - ARA-1 Agent

## Deployment Options

### 1. Local Development

**Requirements:**
- Python 3.10+
- pip or conda
- AWS credentials
- Pinecone account

**Steps:**
```bash
# Clone repository
cd ara_agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with credentials

# Initialize
python setup.py

# Run
python -m src.main interactive
```

### 2. Docker Deployment

**Requirements:**
- Docker
- Docker Compose
- AWS credentials
- Pinecone API key

**Steps:**
```bash
# Build image
docker build -t ara-agent:latest .

# Run container
docker run -it \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e PINECONE_API_KEY=your_key \
  -v ./logs:/app/logs \
  ara-agent:latest

# Or use docker-compose
docker-compose up -d
```

**Docker Compose Benefits:**
- Orchestrates Redis cache
- Manages networking
- Persistent volumes
- Easy scaling

### 3. AWS Lambda Deployment

**Package Structure:**
```
lambda_function.zip
├── src/
├── requirements.txt
├── lambda_handler.py
```

**Lambda Handler:**
```python
import json
import asyncio
from src.agents.research_agent import get_agent

def lambda_handler(event, context):
    try:
        # Parse request
        query = event.get('query', '')
        research_type = event.get('research_type', 'general')
        
        # Execute research
        agent = get_agent()
        result = asyncio.run(agent.execute_research(query, research_type))
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

**Deployment:**
```bash
# Create deployment package
zip -r lambda_function.zip src/ requirements.txt lambda_handler.py

# Deploy
aws lambda create-function \
  --function-name ara-agent \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://lambda_function.zip \
  --timeout 300 \
  --memory-size 1024 \
  --environment Variables={AWS_REGION=us-east-1,BEDROCK_MODEL_ID=...}
```

### 4. AWS ECS Deployment

**Task Definition:**
```json
{
  "family": "ara-agent",
  "containerDefinitions": [
    {
      "name": "ara-agent",
      "image": "YOUR_ECR_REPO/ara-agent:latest",
      "memory": 2048,
      "cpu": 1024,
      "essential": true,
      "environment": [
        {"name": "AWS_REGION", "value": "us-east-1"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ara-agent",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

## Production Configuration

### Environment Variables

```env
# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=prod_key
AWS_SECRET_ACCESS_KEY=prod_secret

# Model Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_MAX_TOKENS=4096

# Vector Database (Production)
PINECONE_API_KEY=prod_key
PINECONE_INDEX_NAME=financial-research-prod
PINECONE_ENVIRONMENT=us-east-1

# Agent Settings (Production)
AGENT_MAX_ITERATIONS=20
AGENT_TEMPERATURE=0.6
AGENT_TIMEOUT_SECONDS=600

# Quality Thresholds
QUALITY_THRESHOLD=0.75
HALLUCINATION_THRESHOLD=0.01
MIN_TOOL_EFFICIENCY=0.80

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/ara-agent/ara_agent.log

# Monitoring
SENTRY_DSN=your_sentry_dsn
ENVIRONMENT=production
```

### Performance Optimization

1. **Memory Management**
   - Set `SHORT_TERM_MAX_TOKENS=4000` for memory-constrained environments
   - Enable Redis caching: `REDIS_HOST=localhost`

2. **Request Timeout**
   - Production: 600 seconds (10 minutes)
   - Development: 300 seconds (5 minutes)

3. **Tool Efficiency**
   - Minimum 80% tool success rate
   - Monitor tool failures via logs

4. **Scaling**
   - Horizontal: Docker/Kubernetes replicas
   - Vertical: Increase container resources

## Monitoring & Logging

### Log Locations

**Local:**
```
logs/ara_agent.log
```

**Docker:**
```bash
docker logs ara-agent
```

**AWS CloudWatch:**
```bash
aws logs tail /ecs/ara-agent --follow
```

### Key Metrics to Monitor

```
- Agent response time (target: < 5 min)
- Tool efficiency (target: > 70%)
- Hallucination rate (target: < 2%)
- Memory utilization
- Error recovery rate
- API quota usage
```

### Alert Thresholds

```
WARNING:
  - Response time > 10 minutes
  - Tool efficiency < 60%
  - Hallucination rate > 5%
  - Error rate > 10%

CRITICAL:
  - Response time > 20 minutes
  - Tool efficiency < 40%
  - Hallucination rate > 10%
  - Error rate > 25%
```

## Security Considerations

### Credentials Management

**Never commit credentials:**
```bash
# Use .env file (add to .gitignore)
echo ".env" >> .gitignore

# Or use AWS Secrets Manager
aws secretsmanager create-secret \
  --name ara-agent-creds \
  --secret-string '{"AWS_ACCESS_KEY_ID":"...","AWS_SECRET_ACCESS_KEY":"..."}'
```

### IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeAgent"
      ],
      "Resource": "arn:aws:bedrock:*::*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:ara-agent-*"
    }
  ]
}
```

### Network Security

- Run in VPC (for container deployments)
- Use security groups to restrict access
- Enable encryption in transit (TLS)
- Regular security updates

## Scaling Strategy

### Horizontal Scaling (Multiple Instances)

```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ara-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ara-agent
  template:
    metadata:
      labels:
        app: ara-agent
    spec:
      containers:
      - name: ara-agent
        image: ara-agent:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
```

### Load Balancing

- Use AWS ELB/ALB for HTTP requests
- Distribute across multiple instances
- Share Redis cache backend

## Backup & Recovery

### Data Backup

```bash
# Backup vector database
pinecone-cli backup --index financial-research-prod

# Backup logs
aws s3 sync logs/ s3://ara-agent-backup/logs/

# Backup data
aws s3 sync data/ s3://ara-agent-backup/data/
```

### Recovery Procedure

1. **Agent Failure**
   - Automatic container restart (Docker)
   - CloudWatch alerts trigger investigation

2. **Vector DB Failure**
   - Restore from Pinecone backups
   - Recent queries will fail temporarily
   - Agent continues with degraded memory

3. **Complete System Failure**
   - Restore from latest backup
   - Verify database integrity
   - Run test evaluation suite

## Update & Deployment

### Rolling Updates

```bash
# For Docker Compose
docker-compose up -d --build

# For Kubernetes
kubectl set image deployment/ara-agent \
  ara-agent=ara-agent:v1.1.0 \
  --record

# For Lambda
aws lambda update-function-code \
  --function-name ara-agent \
  --zip-file fileb://lambda_function.zip
```

### Rollback

```bash
# Docker
docker-compose down
docker pull ara-agent:previous
docker-compose up -d

# Kubernetes
kubectl rollout undo deployment/ara-agent

# Lambda
aws lambda update-function-code \
  --function-name ara-agent \
  --zip-file fileb://lambda_function_rollback.zip
```

## Cost Optimization

### AWS Bedrock
- Request pricing per 1M tokens
- Estimate: $0.003/1K input tokens, $0.015/1K output
- Optimize prompt engineering to reduce tokens

### Pinecone
- Free tier: 1 index, 100K vectors
- Pro tier: $70-600/month depending on usage
- Archive old memories to reduce storage

### Data Transfer
- Minimize inter-service calls
- Cache results locally
- Use batch operations where possible

## Troubleshooting Deployment

### Issue: High Memory Usage
```
Solution:
1. Reduce SHORT_TERM_MAX_TOKENS
2. Enable Redis caching
3. Increase container memory limits
```

### Issue: Slow Response Times
```
Solution:
1. Check Bedrock API latency
2. Verify network connectivity
3. Reduce AGENT_MAX_ITERATIONS
4. Check tool cache hit rates
```

### Issue: API Rate Limiting
```
Solution:
1. Implement request queuing
2. Increase API quotas with providers
3. Add exponential backoff
4. Distribute across multiple API keys
```

## Maintenance Schedule

**Daily:**
- Monitor error rates
- Check log files
- Verify API connectivity

**Weekly:**
- Review performance metrics
- Backup vector database
- Update dependency checks

**Monthly:**
- Full system health check
- Security audit
- Performance optimization review

**Quarterly:**
- Major version updates
- Comprehensive testing
- Capacity planning

---

For questions or issues, refer to:
- README.md - Full documentation
- QUICKSTART.md - Quick setup
- logs/ara_agent.log - Debug information
