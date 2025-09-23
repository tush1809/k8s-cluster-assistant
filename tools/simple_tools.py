"""
Simple function-based tools for LangGraph.
These avoid Pydantic issues by being plain functions.
"""

from typing import Optional, Dict, Any
from k8s_client import KubernetesClient
import json

# Global client instance
_k8s_client = None

def initialize_k8s_client():
    """Initialize the global Kubernetes client."""
    global _k8s_client
    if _k8s_client is None:
        _k8s_client = KubernetesClient()
    return _k8s_client

def list_namespaces() -> str:
    """List all namespaces in the Kubernetes cluster."""
    try:
        client = initialize_k8s_client()
        namespaces = client.list_namespaces()
        
        if not namespaces:
            return "No namespaces found in the cluster."
        
        response = f"Found {len(namespaces)} namespaces:\n\n"
        for ns in namespaces:
            response += f"• **{ns['name']}** (Status: {ns['status']})\n"
            if ns['created']:
                response += f"  Created: {ns['created']}\n"
        
        return response
        
    except Exception as e:
        return f"Error retrieving namespaces: {str(e)}"

def list_pods(namespace: Optional[str] = None) -> str:
    """List pods in the Kubernetes cluster, optionally filtered by namespace."""
    try:
        client = initialize_k8s_client()
        pods = client.list_pods(namespace=namespace)
        
        if not pods:
            ns_text = f" in namespace '{namespace}'" if namespace else ""
            return f"No pods found{ns_text}."
        
        # Group pods by status for better readability
        status_groups = {}
        for pod in pods:
            status = pod['status']
            status_groups.setdefault(status, []).append(pod)
        
        ns_text = f" in namespace '{namespace}'" if namespace else ""
        response = f"Found {len(pods)} pods{ns_text}:\n\n"
        
        for status, pod_list in status_groups.items():
            response += f"**{status} ({len(pod_list)} pods):**\n"
            for pod in pod_list:
                ready_text = "✓" if pod['ready'] else "✗"
                response += f"• {pod['name']} ({pod['namespace']}) {ready_text}"
                if pod['restarts'] > 0:
                    response += f" [Restarts: {pod['restarts']}]"
                response += "\n"
            response += "\n"
        
        return response
        
    except Exception as e:
        return f"Error retrieving pods: {str(e)}"

def list_nodes() -> str:
    """List all nodes in the Kubernetes cluster."""
    try:
        client = initialize_k8s_client()
        nodes = client.list_nodes()
        
        if not nodes:
            return "No nodes found in the cluster."
        
        ready_nodes = len([n for n in nodes if n['status'] == 'Ready'])
        response = f"Found {len(nodes)} nodes ({ready_nodes} ready):\n\n"
        
        for node in nodes:
            status_icon = "✓" if node['status'] == 'Ready' else "✗"
            roles = ", ".join(node['roles']) if node['roles'] else "worker"
            
            response += f"• **{node['name']}** {status_icon}\n"
            response += f"  Roles: {roles}\n"
            response += f"  Version: {node['version']}\n"
            response += f"  OS: {node['os']} ({node['architecture']})\n"
            if node['allocatable_cpu'] and node['allocatable_memory']:
                response += f"  Resources: {node['allocatable_cpu']} CPU, {node['allocatable_memory']} memory\n"
            response += "\n"
        
        return response
        
    except Exception as e:
        return f"Error retrieving nodes: {str(e)}"

def list_services(namespace: Optional[str] = None) -> str:
    """List services in the Kubernetes cluster, optionally filtered by namespace."""
    try:
        client = initialize_k8s_client()
        services = client.list_services(namespace=namespace)
        
        if not services:
            ns_text = f" in namespace '{namespace}'" if namespace else ""
            return f"No services found{ns_text}."
        
        # Group services by type
        type_groups = {}
        for svc in services:
            type_groups.setdefault(svc['type'], []).append(svc)
        
        ns_text = f" in namespace '{namespace}'" if namespace else ""
        response = f"Found {len(services)} services{ns_text}:\n\n"
        
        for svc_type, svc_list in type_groups.items():
            response += f"**{svc_type} ({len(svc_list)} services):**\n"
            for svc in svc_list:
                response += f"• **{svc['name']}** ({svc['namespace']})\n"
                response += f"  Cluster IP: {svc['cluster_ip']}\n"
                if svc['ports']:
                    ports = ", ".join([f"{p['port']}/{p['protocol']}" for p in svc['ports']])
                    response += f"  Ports: {ports}\n"
                if svc['external_ips']:
                    response += f"  External IPs: {', '.join(svc['external_ips'])}\n"
            response += "\n"
        
        return response
        
    except Exception as e:
        return f"Error retrieving services: {str(e)}"

def get_cluster_info() -> str:
    """Get general information and statistics about the Kubernetes cluster."""
    try:
        client = initialize_k8s_client()
        cluster_info = client.get_cluster_info()
        
        response = "**Cluster Overview:**\n\n"
        response += f"• **Namespaces:** {cluster_info['total_namespaces']}\n"
        response += f"• **Pods:** {cluster_info['total_pods']} total, {cluster_info['running_pods']} running\n"
        response += f"• **Nodes:** {cluster_info['total_nodes']} total, {cluster_info['ready_nodes']} ready\n"
        response += f"• **Services:** {cluster_info['total_services']}\n\n"
        
        if cluster_info['node_versions']:
            versions = ", ".join(cluster_info['node_versions'])
            response += f"**Kubernetes Versions:** {versions}\n\n"
        
        if cluster_info['namespaces']:
            ns_list = ", ".join(cluster_info['namespaces'][:10])
            if len(cluster_info['namespaces']) > 10:
                ns_list += f" (and {len(cluster_info['namespaces']) - 10} more)"
            response += f"**Namespaces:** {ns_list}\n"
        
        return response
        
    except Exception as e:
        return f"Error retrieving cluster information: {str(e)}"

# Tool registry for LangGraph
AVAILABLE_TOOLS = {
    "list_namespaces": {
        "function": list_namespaces,
        "description": "List all namespaces in the Kubernetes cluster",
        "parameters": {}
    },
    "list_pods": {
        "function": list_pods,
        "description": "List pods in the cluster, optionally filtered by namespace",
        "parameters": {
            "namespace": {"type": "string", "description": "Optional namespace to filter pods", "required": False}
        }
    },
    "list_nodes": {
        "function": list_nodes,
        "description": "List all nodes in the Kubernetes cluster",
        "parameters": {}
    },
    "list_services": {
        "function": list_services,
        "description": "List services in the cluster, optionally filtered by namespace",
        "parameters": {
            "namespace": {"type": "string", "description": "Optional namespace to filter services", "required": False}
        }
    },
    "get_cluster_info": {
        "function": get_cluster_info,
        "description": "Get general cluster overview and statistics",
        "parameters": {}
    }
}
