"""
LangChain tools for Kubernetes cluster operations.
These tools wrap the Kubernetes client functions for use with LLM agents.
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, List, Dict, Any
import json
from k8s_client import KubernetesClient


class ListNamespacesInput(BaseModel):
    """Input for list_namespaces tool."""
    pass


class ListPodsInput(BaseModel):
    """Input for list_pods tool."""
    namespace: Optional[str] = Field(
        default=None,
        description="Optional namespace to filter pods. If not provided, lists all pods in all namespaces."
    )


class ListNodesInput(BaseModel):
    """Input for list_nodes tool."""
    pass


class ListServicesInput(BaseModel):
    """Input for list_services tool."""
    namespace: Optional[str] = Field(
        default=None,
        description="Optional namespace to filter services. If not provided, lists all services in all namespaces."
    )


class GetClusterInfoInput(BaseModel):
    """Input for get_cluster_info tool."""
    pass


class KubernetesListNamespacesTool(BaseTool):
    """Tool for listing Kubernetes namespaces."""
    
    name = "list_namespaces"
    description = """
    List all namespaces in the Kubernetes cluster.
    Use this tool when users ask about namespaces, want to see what namespaces exist,
    or need to understand the cluster organization.
    Returns information about namespace names, status, creation time, and labels.
    """
    args_schema: Type[BaseModel] = ListNamespacesInput
    
    def __init__(self, k8s_client: KubernetesClient):
        super().__init__()
        self.k8s_client = k8s_client
    
    def _run(self) -> str:
        """Execute the tool."""
        try:
            namespaces = self.k8s_client.list_namespaces()
            
            if not namespaces:
                return "No namespaces found in the cluster."
            
            # Format response for readability
            response = f"Found {len(namespaces)} namespaces:\n\n"
            for ns in namespaces:
                response += f"• **{ns['name']}** (Status: {ns['status']})\n"
                if ns['created']:
                    response += f"  Created: {ns['created']}\n"
            
            return response
            
        except Exception as e:
            return f"Error retrieving namespaces: {str(e)}"


class KubernetesListPodsTool(BaseTool):
    """Tool for listing Kubernetes pods."""
    
    name = "list_pods"
    description = """
    List pods in the Kubernetes cluster, optionally filtered by namespace.
    Use this tool when users ask about pods, running containers, pod status,
    or want to see what applications are deployed.
    Returns information about pod names, namespaces, status, readiness, and restart counts.
    """
    args_schema: Type[BaseModel] = ListPodsInput
    
    def __init__(self, k8s_client: KubernetesClient):
        super().__init__()
        self.k8s_client = k8s_client
    
    def _run(self, namespace: Optional[str] = None) -> str:
        """Execute the tool."""
        try:
            pods = self.k8s_client.list_pods(namespace=namespace)
            
            if not pods:
                ns_text = f" in namespace '{namespace}'" if namespace else ""
                return f"No pods found{ns_text}."
            
            # Group pods by status for better readability
            status_groups = {}
            for pod in pods:
                status = pod['status']
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(pod)
            
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


class KubernetesListNodesTool(BaseTool):
    """Tool for listing Kubernetes nodes."""
    
    name = "list_nodes"
    description = """
    List all nodes in the Kubernetes cluster.
    Use this tool when users ask about nodes, cluster capacity, node status,
    or infrastructure information.
    Returns information about node names, status, roles, versions, and resource capacity.
    """
    args_schema: Type[BaseModel] = ListNodesInput
    
    def __init__(self, k8s_client: KubernetesClient):
        super().__init__()
        self.k8s_client = k8s_client
    
    def _run(self) -> str:
        """Execute the tool."""
        try:
            nodes = self.k8s_client.list_nodes()
            
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


class KubernetesListServicesTool(BaseTool):
    """Tool for listing Kubernetes services."""
    
    name = "list_services"
    description = """
    List services in the Kubernetes cluster, optionally filtered by namespace.
    Use this tool when users ask about services, network endpoints, load balancers,
    or how applications are exposed.
    Returns information about service names, types, IPs, and ports.
    """
    args_schema: Type[BaseModel] = ListServicesInput
    
    def __init__(self, k8s_client: KubernetesClient):
        super().__init__()
        self.k8s_client = k8s_client
    
    def _run(self, namespace: Optional[str] = None) -> str:
        """Execute the tool."""
        try:
            services = self.k8s_client.list_services(namespace=namespace)
            
            if not services:
                ns_text = f" in namespace '{namespace}'" if namespace else ""
                return f"No services found{ns_text}."
            
            # Group services by type
            type_groups = {}
            for svc in services:
                svc_type = svc['type']
                if svc_type not in type_groups:
                    type_groups[svc_type] = []
                type_groups[svc_type].append(svc)
            
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


class KubernetesGetClusterInfoTool(BaseTool):
    """Tool for getting general cluster information."""
    
    name = "get_cluster_info"
    description = """
    Get general information and statistics about the Kubernetes cluster.
    Use this tool when users ask for cluster overview, summary, general stats,
    or want to understand the overall cluster state.
    Returns counts of namespaces, pods, nodes, services, and other summary information.
    """
    args_schema: Type[BaseModel] = GetClusterInfoInput
    
    def __init__(self, k8s_client: KubernetesClient):
        super().__init__()
        self.k8s_client = k8s_client
    
    def _run(self) -> str:
        """Execute the tool."""
        try:
            cluster_info = self.k8s_client.get_cluster_info()
            
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


def get_kubernetes_tools(k8s_client: KubernetesClient) -> List[BaseTool]:
    """Return a list of all Kubernetes tools, sharing the same client instance."""
    return [
        KubernetesListNamespacesTool(k8s_client),
        KubernetesListPodsTool(k8s_client),
        KubernetesListNodesTool(k8s_client),
        KubernetesListServicesTool(k8s_client),
        KubernetesGetClusterInfoTool(k8s_client)
    ]
