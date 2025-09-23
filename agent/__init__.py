"""
Kubernetes agent module with LangGraph integration.
"""

# Import the new LangGraph agent
from .langgraph_agent import KubernetesGraphAgent, create_kubernetes_agent

# Export the LangGraph agent as the main agent
KubernetesAgent = KubernetesGraphAgent

# Keep the factory function
__all__ = ['KubernetesAgent', 'create_kubernetes_agent']
