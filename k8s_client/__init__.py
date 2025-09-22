"""
Kubernetes client module for retrieving cluster information.
Provides functions to query pods, namespaces, nodes, and services.
"""

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KubernetesClient:
    """Kubernetes client for cluster information retrieval."""
    
    def __init__(self):
        """Initialize Kubernetes client with cluster configuration."""
        try:
            # Try to load in-cluster config first (for pods running in cluster)
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes configuration")
        except config.ConfigException:
            try:
                # Fall back to local kubeconfig
                config.load_kube_config()
                logger.info("Loaded local Kubernetes configuration")
            except config.ConfigException as e:
                logger.error(f"Failed to load Kubernetes configuration: {e}")
                raise
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
    
    def list_namespaces(self) -> List[Dict[str, Any]]:
        """
        List all namespaces in the cluster.
        
        Returns:
            List of namespace information dictionaries
        """
        try:
            namespaces = self.v1.list_namespace()
            namespace_list = []
            
            for ns in namespaces.items:
                namespace_info = {
                    "name": ns.metadata.name,
                    "status": ns.status.phase,
                    "created": ns.metadata.creation_timestamp.isoformat() if ns.metadata.creation_timestamp else None,
                    "labels": ns.metadata.labels or {}
                }
                namespace_list.append(namespace_info)
            
            logger.info(f"Retrieved {len(namespace_list)} namespaces")
            return namespace_list
            
        except ApiException as e:
            logger.error(f"Error listing namespaces: {e}")
            raise
    
    def list_pods(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List pods in the cluster or specific namespace.
        
        Args:
            namespace: Optional namespace to filter pods. If None, lists all pods.
            
        Returns:
            List of pod information dictionaries
        """
        try:
            if namespace:
                pods = self.v1.list_namespaced_pod(namespace=namespace)
            else:
                pods = self.v1.list_pod_for_all_namespaces()
            
            pod_list = []
            
            for pod in pods.items:
                pod_info = {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "ready": self._is_pod_ready(pod),
                    "restarts": sum(container.restart_count for container in pod.status.container_statuses or []),
                    "created": pod.metadata.creation_timestamp.isoformat() if pod.metadata.creation_timestamp else None,
                    "node": pod.spec.node_name,
                    "containers": [c.name for c in pod.spec.containers]
                }
                pod_list.append(pod_info)
            
            logger.info(f"Retrieved {len(pod_list)} pods")
            return pod_list
            
        except ApiException as e:
            logger.error(f"Error listing pods: {e}")
            raise
    
    def list_nodes(self) -> List[Dict[str, Any]]:
        """
        List all nodes in the cluster.
        
        Returns:
            List of node information dictionaries
        """
        try:
            nodes = self.v1.list_node()
            node_list = []
            
            for node in nodes.items:
                # Get node conditions
                conditions = {}
                for condition in node.status.conditions or []:
                    conditions[condition.type] = condition.status
                
                node_info = {
                    "name": node.metadata.name,
                    "status": "Ready" if conditions.get("Ready") == "True" else "NotReady",
                    "roles": self._get_node_roles(node),
                    "version": node.status.node_info.kubelet_version,
                    "os": node.status.node_info.operating_system,
                    "architecture": node.status.node_info.architecture,
                    "created": node.metadata.creation_timestamp.isoformat() if node.metadata.creation_timestamp else None,
                    "allocatable_cpu": node.status.allocatable.get("cpu"),
                    "allocatable_memory": node.status.allocatable.get("memory")
                }
                node_list.append(node_info)
            
            logger.info(f"Retrieved {len(node_list)} nodes")
            return node_list
            
        except ApiException as e:
            logger.error(f"Error listing nodes: {e}")
            raise
    
    def list_services(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List services in the cluster or specific namespace.
        
        Args:
            namespace: Optional namespace to filter services. If None, lists all services.
            
        Returns:
            List of service information dictionaries
        """
        try:
            if namespace:
                services = self.v1.list_namespaced_service(namespace=namespace)
            else:
                services = self.v1.list_service_for_all_namespaces()
            
            service_list = []
            
            for svc in services.items:
                service_info = {
                    "name": svc.metadata.name,
                    "namespace": svc.metadata.namespace,
                    "type": svc.spec.type,
                    "cluster_ip": svc.spec.cluster_ip,
                    "external_ips": svc.spec.external_i_ps or [],
                    "ports": [
                        {
                            "port": port.port,
                            "target_port": str(port.target_port) if port.target_port else None,
                            "protocol": port.protocol
                        }
                        for port in svc.spec.ports or []
                    ],
                    "selector": svc.spec.selector or {},
                    "created": svc.metadata.creation_timestamp.isoformat() if svc.metadata.creation_timestamp else None
                }
                service_list.append(service_info)
            
            logger.info(f"Retrieved {len(service_list)} services")
            return service_list
            
        except ApiException as e:
            logger.error(f"Error listing services: {e}")
            raise
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get general cluster information.
        
        Returns:
            Dictionary with cluster summary information
        """
        try:
            # Get basic counts
            namespaces = self.list_namespaces()
            pods = self.list_pods()
            nodes = self.list_nodes()
            services = self.list_services()
            
            # Calculate statistics
            running_pods = len([p for p in pods if p["status"] == "Running"])
            ready_nodes = len([n for n in nodes if n["status"] == "Ready"])
            
            cluster_info = {
                "total_namespaces": len(namespaces),
                "total_pods": len(pods),
                "running_pods": running_pods,
                "total_nodes": len(nodes),
                "ready_nodes": ready_nodes,
                "total_services": len(services),
                "node_versions": list(set(n["version"] for n in nodes)),
                "namespaces": [ns["name"] for ns in namespaces]
            }
            
            logger.info("Retrieved cluster summary information")
            return cluster_info
            
        except Exception as e:
            logger.error(f"Error getting cluster info: {e}")
            raise
    
    def _is_pod_ready(self, pod) -> bool:
        """Check if a pod is ready."""
        if not pod.status.conditions:
            return False
        
        for condition in pod.status.conditions:
            if condition.type == "Ready":
                return condition.status == "True"
        return False
    
    def _get_node_roles(self, node) -> List[str]:
        """Extract node roles from labels."""
        roles = []
        labels = node.metadata.labels or {}
        
        for label_key in labels:
            if label_key.startswith("node-role.kubernetes.io/"):
                role = label_key.replace("node-role.kubernetes.io/", "")
                if role:
                    roles.append(role)
        
        return roles if roles else ["worker"]
