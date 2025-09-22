# 🚀 Kubernetes Cluster Assistant

A modern, natural language interface for querying AWS EKS cluster information using AWS Bedrock and LangChain. This project provides both CLI and web interfaces to make Kubernetes cluster information accessible through conversational AI.

![GitHub repo size](https://img.shields.io/github/repo-size/tush1809/k8s-cluster-assistant)
![GitHub last commit](https://img.shields.io/github/last-commit/tush1809/k8s-cluster-assistant)
![GitHub issues](https://img.shields.io/github/issues/tush1809/k8s-cluster-assistant)

## 🌟 Features

### 🎯 **Natural Language Queries**
- Ask questions in plain English about your Kubernetes cluster
- Get formatted, human-readable responses
- No need to remember kubectl commands or complex syntax

### 🌐 **Dual Interface**
- **CLI Mode**: Command-line interface for terminal users
- **Web Interface**: Beautiful, modern web dashboard with real-time chat

### 🔐 **Secure & Read-Only**
- Only retrieves cluster information (no modifications)
- Proper RBAC permissions required
- No sensitive data exposure

### 🤖 **AI-Powered**
- Uses AWS Bedrock (Claude-3-Haiku/Sonnet) for natural language understanding
- LangChain integration for tool orchestration
- Context-aware responses with explanations

## 📸 Screenshots

### Web Interface
```
🚀 Kubernetes Cluster Interface
   Ask questions about your cluster in natural language

┌─────────────────────────────────────────────────────────────┐
│ ● System Ready                           2025-09-22 10:30 │
├─────────────────────────────────────────────────────────────┤
│                    💬 Chat Interface                        │
│ ┌─────────────────────────────────────┬─────────────────── │
│ │ 🤖 Kubernetes Assistant            │  💡 Example Queries │
│ │                                     │                   │
│ │ You: How many pods are running?     │  • What's the...  │
│ │                                     │  • Show me pods   │
│ │ Bot: Found 45 pods across all...   │  • List nodes     │
│ │                                     │                   │
│ │ [Type your question here...    ] 📤 │  ℹ️ Agent Info    │
│ └─────────────────────────────────────┴─────────────────── │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS CLI configured with Bedrock access
- kubectl configured for your EKS cluster

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tush1809/k8s-cluster-assistant.git
   cd k8s-cluster-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS region and preferences
   ```

4. **Test setup**
   ```bash
   python main.py test
   ```

### Usage Options

#### 🌐 **Web Interface** (Recommended)
```bash
python start_web.py
```
Then open: http://localhost:5000

#### 💻 **CLI Mode**
```bash
# Interactive mode
python main.py interactive

# Single query
python main.py query "How many pods are running?"

# View examples
python demo.py
```

## 💬 Example Queries

- **General**: "What's the cluster overview?"
- **Pods**: "How many pods are running?", "Show me failed pods"
- **Nodes**: "List all nodes", "Are all nodes ready?"
- **Namespaces**: "What namespaces exist?"
- **Services**: "Show me services in default namespace"

## 🏗️ Architecture

```
User Query → LangChain Agent → Kubernetes Tools → EKS Cluster
                ↓
AWS Bedrock LLM ← Response Formatting ← Raw Data
```

### Components

- **`k8s_client/`**: Kubernetes API wrapper with read-only operations
- **`tools/`**: LangChain tools for cluster operations
- **`bedrock/`**: AWS Bedrock LLM integration
- **`agent/`**: Natural language agent orchestration
- **`web/`**: Flask web interface with modern UI

## 🔧 Configuration

### AWS Permissions
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
        }
    ]
}
```

### Kubernetes RBAC
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-info-reader
rules:
- apiGroups: [""]
  resources: ["namespaces", "pods", "nodes", "services"]
  verbs: ["get", "list"]
```

## 🛠️ Development

### Project Structure
```
k8s-cluster-assistant/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── main.py                   # CLI interface
├── start_web.py             # Web interface launcher
├── demo.py                  # Demo script
├── k8s_client/              # Kubernetes client
├── tools/                   # LangChain tools
├── bedrock/                 # AWS Bedrock integration
├── agent/                   # Natural language agent
└── web/                     # Web interface
    ├── app.py               # Flask backend
    └── templates/           # HTML templates
```

### Available Scripts
- `python main.py test` - Test configuration
- `python main.py models` - List available models
- `python check_environment.py` - Environment diagnostics
- `python demo.py` - Run demonstration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [AWS Bedrock](https://aws.amazon.com/bedrock/) for LLM capabilities
- [LangChain](https://langchain.com/) for agent orchestration
- [Kubernetes Python Client](https://github.com/kubernetes-client/python) for cluster access
- [Flask](https://flask.palletsprojects.com/) for web interface

## 📞 Support

- Create an [Issue](https://github.com/tush1809/k8s-cluster-assistant/issues) for bug reports
- Check [Discussions](https://github.com/tush1809/k8s-cluster-assistant/discussions) for questions
- Review [SETUP.md](SETUP.md) for detailed configuration

---

**Made with ❤️ for the Kubernetes community**
