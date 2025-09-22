# Kubernetes Cluster Information Interface

A natural language interface for querying AWS EKS cluster information using AWS Bedrock and LangChain.

## Overview

This project provides a conversational AI interface that allows users to query basic Kubernetes cluster information without requiring direct cluster access. Users can ask questions in natural language like "How many pods are running?" or "List all namespaces" and receive formatted responses.

## Features

- Natural language querying of Kubernetes cluster information
- Secure data access layer using Kubernetes Python client
- LangChain tool integration for LLM accessibility
- AWS Bedrock integration for advanced language understanding
- Human-readable response formatting

## Architecture

```
User Query → LangChain Agent → Kubernetes Tools → EKS Cluster
                ↓
AWS Bedrock LLM ← Response Formatting ← Raw Data
```

## Components

1. **Kubernetes Data Access Layer** (`k8s_client/`)
   - Functions to retrieve cluster information
   - Pod, namespace, node, and service queries
   - Error handling and data validation

2. **LangChain Tools** (`tools/`)
   - Wrapper functions for Kubernetes operations
   - Tool descriptions for LLM understanding
   - Input/output validation

3. **AWS Bedrock Integration** (`bedrock/`)
   - LLM configuration and initialization
   - Model selection and parameter tuning
   - Response generation

4. **Natural Language Agent** (`agent/`)
   - Query interpretation
   - Tool selection logic
   - Response formatting

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure AWS credentials and Kubernetes access:
   ```bash
   aws configure
   kubectl config current-context
   ```

3. Set environment variables:
   ```bash
   export AWS_REGION=us-west-2
   export BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
   ```

4. Run the interface:
   ```bash
   python main.py
   ```

## Usage Examples

- "How many pods are running?"
- "List all namespaces"
- "What nodes are available?"
- "Show me pods in the default namespace"
- "Are there any failed pods?"

## Requirements

- Python 3.8+
- AWS CLI configured
- kubectl configured for EKS cluster
- Appropriate IAM permissions for Bedrock and EKS

## Security

This interface provides read-only access to cluster information and does not expose sensitive data or administrative capabilities.
