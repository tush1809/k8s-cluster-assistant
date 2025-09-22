# Kubernetes Cluster Information Interface - Setup Guide

## Prerequisites

Before setting up the project, ensure you have the following:

### 1. Python Environment
- Python 3.8 or higher
- pip package manager

### 2. AWS Configuration
- AWS CLI installed and configured
- AWS credentials with appropriate permissions
- Access to AWS Bedrock service

### 3. Kubernetes Access
- kubectl installed and configured
- Access to your EKS cluster
- Appropriate RBAC permissions for cluster information

## Required AWS Permissions

Your AWS IAM user/role needs the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "eks:DescribeCluster",
                "eks:ListClusters"
            ],
            "Resource": "*"
        }
    ]
}
```

## Required Kubernetes Permissions

Your kubeconfig should have permissions to read cluster resources:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-info-reader
rules:
- apiGroups: [""]
  resources: ["namespaces", "pods", "nodes", "services"]
  verbs: ["get", "list"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list"]
```

## Installation Steps

### 1. Clone and Setup
```bash
# Navigate to project directory
cd c:\Users\299776\Desktop\Kubernetes-pods-project

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure AWS
```bash
# Configure AWS credentials if not already done
aws configure

# Test AWS access
aws sts get-caller-identity

# Test Bedrock access
aws bedrock list-foundation-models --region us-west-2
```

### 3. Configure Kubernetes
```bash
# Test kubectl access
kubectl cluster-info

# Test permissions
kubectl get namespaces
kubectl get pods --all-namespaces
```

### 4. Environment Variables (Optional)
Copy `.env.example` to `.env` and customize:
```bash
copy .env.example .env
```

Edit `.env` file:
```
AWS_REGION=us-west-2
BEDROCK_MODEL_NAME=claude-3-haiku
```

### 5. Test Setup
```bash
# Test the complete setup
python main.py test

# Run demo
python demo.py
```

## Usage

### Interactive Mode
```bash
python main.py interactive
```

### Single Query
```bash
python main.py query "How many pods are running?"
```

### Available Models
```bash
python main.py models
```

## Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   ```
   Error: AWS credentials not found
   ```
   Solution: Run `aws configure` or set environment variables

2. **Bedrock Access Denied**
   ```
   Error: Access denied to Bedrock service
   ```
   Solution: Check IAM permissions for Bedrock

3. **Kubernetes Connection Error**
   ```
   Error: Failed to load Kubernetes configuration
   ```
   Solution: Run `kubectl config current-context` and verify cluster access

4. **Model Not Available**
   ```
   Error: Model not available in region
   ```
   Solution: Check if the Bedrock model is available in your region

### Verification Commands

```bash
# Check AWS configuration
aws configure list

# Check Bedrock models
aws bedrock list-foundation-models --region us-west-2

# Check Kubernetes access
kubectl auth can-i get pods --all-namespaces

# Check cluster info
kubectl cluster-info
```

## Security Considerations

1. **Read-Only Access**: The tool only requires read permissions
2. **No Sensitive Data**: Responses don't include sensitive cluster information
3. **Network Security**: Ensure proper network policies for cluster access
4. **IAM Permissions**: Use least-privilege principles for AWS permissions

## Performance Notes

1. **Model Selection**: Claude-3-Haiku is faster and cheaper than Sonnet
2. **Query Optimization**: Use specific queries for better performance
3. **Caching**: Consider implementing caching for frequently accessed data

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Verify AWS and Kubernetes permissions
3. Run the test command to identify configuration issues
