"""
Natural Language Agent for Kubernetes cluster queries.
Uses LangChain agent with Bedrock LLM and Kubernetes tools.
"""

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from typing import List, Dict, Any
import logging

from bedrock import create_bedrock_llm
from tools import get_kubernetes_tools
from kubernetes import client as k8s_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KubernetesAgent:
    """Natural language agent for Kubernetes cluster information queries."""
    
    SYSTEM_PROMPT = """
You are a helpful Kubernetes cluster information assistant. You can help users get information about their Kubernetes cluster by answering questions in natural language.

You have access to several tools that can retrieve information from a Kubernetes cluster:
- list_namespaces: Get all namespaces in the cluster
- list_pods: Get pods, optionally filtered by namespace
- list_nodes: Get all nodes in the cluster
- list_services: Get services, optionally filtered by namespace
- get_cluster_info: Get general cluster overview and statistics

Guidelines for responses:
1. Be conversational and helpful
2. Use the appropriate tool based on the user's question
3. Format responses in a clear, readable way using markdown
4. If a user asks a vague question, use get_cluster_info for an overview
5. For specific questions about pods, nodes, namespaces, or services, use the specific tools
6. Always provide context and explain what the information means
7. If there are issues or no resources found, explain this clearly
8. Use emojis sparingly to make responses more friendly

Example interactions:
- "How many pods are running?" → Use list_pods and get_cluster_info
- "List all namespaces" → Use list_namespaces
- "What's the status of my cluster?" → Use get_cluster_info
- "Show me pods in the default namespace" → Use list_pods with namespace="default"
- "Are all nodes ready?" → Use list_nodes

Remember to be helpful and provide actionable information when possible.
"""
    
    def __init__(self, model_name: str = "claude-3-haiku", region: str = None):
        """
        Initialize the Kubernetes agent.
        
        Args:
            model_name: Bedrock model to use
            region: AWS region for Bedrock
        """
        self.model_name = model_name
        self.region = region
        # Initialize components
        self.bedrock_llm = create_bedrock_llm(model_name, region)
        self.k8s_client = k8s_client
        self.tools = get_kubernetes_tools(self.k8s_client)
        self.agent_executor = None
        self._setup_agent()
    
    def _setup_agent(self):
        """Set up the LangChain agent with tools and prompt."""
        try:
            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=self.SYSTEM_PROMPT),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])
            
            # Get the LLM
            llm = self.bedrock_llm.get_llm()
            
            # Create the agent
            agent = create_tool_calling_agent(
                llm=llm,
                tools=self.tools,
                prompt=prompt
            )
            
            # Create the agent executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                max_iterations=3,
                early_stopping_method="generate"
            )
            
            logger.info("Kubernetes agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up agent: {e}")
            raise
    
    def query(self, user_input: str) -> str:
        """
        Process a natural language query about the Kubernetes cluster.
        
        Args:
            user_input: User's natural language question
            
        Returns:
            Formatted response with cluster information
        """
        if not self.agent_executor:
            raise RuntimeError("Agent not initialized")
        
        try:
            logger.info(f"Processing query: {user_input}")
            
            # Execute the agent
            result = self.agent_executor.invoke({
                "input": user_input
            })
            
            response = result.get("output", "I couldn't process your request.")
            logger.info("Query processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def get_available_commands(self) -> List[str]:
        """
        Get a list of example commands that users can try.
        
        Returns:
            List of example command strings
        """
        return [
            "How many pods are running?",
            "List all namespaces",
            "What nodes are in the cluster?",
            "Show me the cluster overview",
            "Are there any failed pods?",
            "List services in the default namespace",
            "What's the status of my cluster?",
            "How many nodes are ready?",
            "Show me pods in the kube-system namespace",
            "What services are exposed?"
        ]
    
    def test_agent(self) -> bool:
        """
        Test the agent with a simple query.
        
        Returns:
            True if test is successful, False otherwise
        """
        try:
            test_query = "What's the cluster overview?"
            response = self.query(test_query)
            return "error" not in response.lower()
        except Exception as e:
            logger.error(f"Agent test failed: {e}")
            return False
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent configuration."""
        return {
            "model_name": self.model_name,
            "region": self.region,
            "available_tools": [tool.name for tool in self.tools],
            "model_info": self.bedrock_llm.get_model_info()
        }


def create_kubernetes_agent(model_name: str = None, region: str = None) -> KubernetesAgent:
    """
    Factory function to create a KubernetesAgent instance.
    
    Args:
        model_name: Bedrock model to use
        region: AWS region for Bedrock
        
    Returns:
        Initialized KubernetesAgent instance
    """
    return KubernetesAgent(model_name=model_name, region=region)
