"""
Demo script to showcase the Kubernetes cluster information interface.
This script demonstrates various queries and responses.
"""

import sys
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import create_kubernetes_agent

console = Console()


def demo_queries():
    """Predefined demo queries to showcase capabilities."""
    return [
        {
            "query": "What's the cluster overview?",
            "description": "Get general cluster information and statistics"
        },
        {
            "query": "List all namespaces",
            "description": "Show all namespaces in the cluster"
        },
        {
            "query": "How many pods are running?",
            "description": "Count running pods across all namespaces"
        },
        {
            "query": "Show me the nodes in the cluster",
            "description": "Display node information and status"
        },
        {
            "query": "List pods in the kube-system namespace",
            "description": "Show system pods in the kube-system namespace"
        },
        {
            "query": "What services are exposed?",
            "description": "Display all services across namespaces"
        }
    ]


def run_demo():
    """Run the demonstration."""
    
    # Welcome message
    console.print(Panel(
        "🚀 Kubernetes Cluster Information Interface Demo 🚀",
        style="bold blue"
    ))
    console.print()
    
    try:
        # Initialize agent
        console.print("🤖 Initializing the Kubernetes agent...", style="blue")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Setting up agent...", total=None)
            agent = create_kubernetes_agent()
            progress.update(task, description="Agent ready!")
        
        console.print("✅ Agent initialized successfully!", style="green")
        console.print()
        
        # Show agent info
        agent_info = agent.get_agent_info()
        info_panel = Panel(
            f"Model: {agent_info['model_info']['model_id']}\n"
            f"Region: {agent_info['region']}\n"
            f"Available Tools: {', '.join(agent_info['available_tools'])}",
            title="Agent Configuration",
            style="cyan"
        )
        console.print(info_panel)
        console.print()
        
        # Run demo queries
        queries = demo_queries()
        
        for i, demo in enumerate(queries, 1):
            console.print(f"🔍 Demo Query {i}/{len(queries)}", style="bold yellow")
            console.print(f"Description: {demo['description']}", style="dim")
            
            # Show the query
            query_panel = Panel(
                demo['query'],
                title="User Query",
                style="blue"
            )
            console.print(query_panel)
            
            # Execute query with progress
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Processing query...", total=None)
                response = agent.query(demo['query'])
                progress.update(task, description="Complete!")
            
            # Show response
            response_panel = Panel(
                response,
                title="Agent Response",
                style="green"
            )
            console.print(response_panel)
            console.print()
            
            # Pause between queries (except for the last one)
            if i < len(queries):
                console.print("⏳ Moving to next query in 3 seconds...", style="dim")
                time.sleep(3)
                console.print()
        
        # Demo completion
        completion_panel = Panel(
            "🎉 Demo completed successfully!\n\n"
            "The Kubernetes cluster information interface is working correctly.\n"
            "Users can now ask natural language questions about their cluster\n"
            "and receive formatted, helpful responses.\n\n"
            "To start the interactive mode, run: python main.py interactive",
            title="Demo Complete",
            style="bold green"
        )
        console.print(completion_panel)
        
    except Exception as e:
        error_panel = Panel(
            f"❌ Demo failed: {str(e)}\n\n"
            "Common issues:\n"
            "1. AWS credentials not configured\n"
            "2. kubectl not configured for cluster\n"
            "3. Insufficient permissions for Bedrock or EKS\n\n"
            "Please check your configuration and try again.",
            title="Demo Error",
            style="red"
        )
        console.print(error_panel)
        return False
    
    return True


if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)
