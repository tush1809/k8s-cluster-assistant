"""
LangGraph-based Kubernetes agent.
Simple and reliable without Pydantic complexities.
"""

import json
import re
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.schema import BaseMessage
import logging

from bedrock import create_bedrock_llm
from tools.simple_tools import AVAILABLE_TOOLS, initialize_k8s_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KubernetesGraphAgent:
    """LangGraph-based Kubernetes assistant."""
    
    SYSTEM_PROMPT = """
You are a helpful Kubernetes cluster information assistant. You can help users get information about their Kubernetes cluster by answering questions in natural language.

You have access to these tools:
- list_namespaces: Get all namespaces in the cluster
- list_pods: Get pods, optionally filtered by namespace  
- list_nodes: Get all nodes in the cluster
- list_services: Get services, optionally filtered by namespace
- get_cluster_info: Get general cluster overview and statistics

To use a tool, respond with JSON in this format:
{"tool": "tool_name", "parameters": {"param": "value"}}

Guidelines:
1. Be conversational and helpful
2. Use the appropriate tool based on the user's question
3. Format responses clearly using markdown
4. If a user asks a vague question, use get_cluster_info for an overview
5. For specific questions about pods, nodes, namespaces, or services, use the specific tools
6. Always provide context and explain what the information means
7. If there are issues or no resources found, explain this clearly

Example interactions:
- "How many pods are running?" → Use get_cluster_info or list_pods
- "List all namespaces" → Use list_namespaces
- "What's the status of my cluster?" → Use get_cluster_info
- "Show me pods in the default namespace" → Use list_pods with namespace="default"
- "Are all nodes ready?" → Use list_nodes
"""
    
    def __init__(self, model_name: str = "claude-3-haiku", region: str = None):
        """Initialize the LangGraph agent."""
        self.model_name = model_name
        self.region = region
        
        # Initialize components
        self.bedrock_llm = create_bedrock_llm(model_name, region)
        self.llm = self.bedrock_llm.get_llm()
        
        # Initialize K8s client
        initialize_k8s_client()
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info("LangGraph Kubernetes agent initialized successfully")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        
        def agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """Main agent reasoning node."""
            messages = state.get("messages", [])
            
            # Add system message if not present
            if not any(isinstance(msg, SystemMessage) for msg in messages):
                messages = [SystemMessage(content=self.SYSTEM_PROMPT)] + messages
            
            # Get LLM response
            response = self.llm.invoke(messages)
            
            # Check if response contains tool call
            tool_call = self._parse_tool_call(response.content)
            
            if tool_call:
                state["tool_call"] = tool_call
                state["messages"] = messages + [response]
                return state
            else:
                # Final response
                state["messages"] = messages + [response]
                state["final_response"] = response.content
                return state
        
        def tool_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """Execute tool and return result."""
            tool_call = state.get("tool_call")
            
            if not tool_call:
                return state
            
            tool_name = tool_call["tool"]
            parameters = tool_call.get("parameters", {})
            
            # Execute tool
            if tool_name in AVAILABLE_TOOLS:
                try:
                    tool_func = AVAILABLE_TOOLS[tool_name]["function"]
                    if parameters:
                        result = tool_func(**parameters)
                    else:
                        result = tool_func()
                    
                    # Add tool result to messages
                    tool_message = AIMessage(content=f"Tool {tool_name} result: {result}")
                    state["messages"].append(tool_message)
                    
                except Exception as e:
                    error_message = AIMessage(content=f"Error executing {tool_name}: {str(e)}")
                    state["messages"].append(error_message)
            else:
                error_message = AIMessage(content=f"Unknown tool: {tool_name}")
                state["messages"].append(error_message)
            
            # Clear tool call
            state["tool_call"] = None
            return state
        
        def should_continue(state: Dict[str, Any]) -> str:
            """Decide whether to continue or end."""
            if state.get("tool_call"):
                return "tool"
            elif state.get("final_response"):
                return END
            else:
                return "agent"
        
        # Build graph
        workflow = StateGraph(dict)
        
        workflow.add_node("agent", agent_node)
        workflow.add_node("tool", tool_node)
        
        workflow.set_entry_point("agent")
        
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tool": "tool",
                END: END,
                "agent": "agent"
            }
        )
        
        workflow.add_edge("tool", "agent")
        
        return workflow.compile()
    
    def _parse_tool_call(self, response: str) -> Dict[str, Any]:
        """Parse tool call from LLM response."""
        try:
            # Look for JSON in the response
            json_match = re.search(r'\{[^}]*"tool"[^}]*\}', response)
            if json_match:
                tool_call = json.loads(json_match.group())
                if "tool" in tool_call:
                    return tool_call
        except json.JSONDecodeError:
            pass
        
        return None
    
    def query(self, user_input: str) -> str:
        """Process a user query."""
        try:
            logger.info(f"Processing query: {user_input}")
            
            # Initialize state
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "tool_call": None,
                "final_response": None
            }
            
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            # Extract final response
            if final_state.get("final_response"):
                return final_state["final_response"]
            elif final_state.get("messages"):
                # Get last AI message
                for msg in reversed(final_state["messages"]):
                    if isinstance(msg, AIMessage):
                        return msg.content
            
            return "I couldn't process your request."
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def get_available_commands(self) -> List[str]:
        """Get example commands."""
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
        """Test the agent."""
        try:
            response = self.query("What's the cluster overview?")
            return "error" not in response.lower()
        except Exception as e:
            logger.error(f"Agent test failed: {e}")
            return False


def create_kubernetes_agent(model_name: str = None, region: str = None) -> KubernetesGraphAgent:
    """Factory function to create a LangGraph Kubernetes agent."""
    model_name = model_name or "claude-3-haiku"
    return KubernetesGraphAgent(model_name=model_name, region=region)
