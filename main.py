"""
Main application entry point.
Command-line interface for the Kubernetes cluster information system.
"""

import click
import os
import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import create_kubernetes_agent
from bedrock import BedrockLLM

# Setup rich console for better output
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise in interactive mode
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def print_welcome():
    """Print welcome message and instructions."""
    welcome_text = Text()
    welcome_text.append("🚀 ", style="bold blue")
    welcome_text.append("Kubernetes Cluster Information Assistant", style="bold green")
    welcome_text.append(" 🚀", style="bold blue")
    
    panel = Panel(
        welcome_text,
        subtitle="Ask questions about your cluster in natural language!",
        style="blue"
    )
    console.print(panel)
    console.print()


def print_examples():
    """Print example queries users can try."""
    table = Table(title="Example Queries", style="cyan")
    table.add_column("Category", style="bold yellow")
    table.add_column("Example Questions", style="white")
    
    examples = [
        ("General", "What's the cluster overview?\nHow is my cluster doing?"),
        ("Pods", "How many pods are running?\nShow me pods in the default namespace\nAre there any failed pods?"),
        ("Nodes", "List all nodes\nHow many nodes are ready?\nWhat's the node status?"),
        ("Namespaces", "List all namespaces\nWhat namespaces exist?"),
        ("Services", "Show me all services\nList services in kube-system namespace")
    ]
    
    for category, examples_text in examples:
        table.add_row(category, examples_text)
    
    console.print(table)
    console.print()


def test_setup() -> bool:
    """Test if all components are properly configured."""
    console.print("🔍 Testing setup...", style="yellow")
    
    try:
        # Test Bedrock connection
        console.print("  Testing AWS Bedrock connection...", end="")
        bedrock_llm = BedrockLLM()
        if bedrock_llm.test_connection():
            console.print(" ✅", style="green")
        else:
            console.print(" ❌", style="red")
            return False
        
        # Test agent initialization
        console.print("  Testing agent initialization...", end="")
        agent = create_kubernetes_agent()
        if agent.test_agent():
            console.print(" ✅", style="green")
        else:
            console.print(" ❌", style="red")
            return False
        
        console.print("✅ Setup test completed successfully!", style="green")
        return True
        
    except Exception as e:
        console.print(f" ❌ Error: {e}", style="red")
        return False


@click.group()
def cli():
    """Kubernetes Cluster Information Interface - Natural Language Queries for EKS"""
    pass


@cli.command()
@click.option('--model', default='claude-3-haiku', 
              help='Bedrock model to use (claude-3-haiku, claude-3-sonnet, titan-text)')
@click.option('--region', default=None, 
              help='AWS region for Bedrock (defaults to AWS_REGION env var or us-west-2)')
@click.option('--test-only', is_flag=True, 
              help='Only test the setup without starting interactive mode')
def interactive(model: str, region: Optional[str], test_only: bool):
    """Start interactive mode for querying cluster information."""
    
    print_welcome()
    
    # Test setup
    if not test_setup():
        console.print("❌ Setup test failed. Please check your configuration.", style="red")
        console.print("\nCommon issues:", style="yellow")
        console.print("1. AWS credentials not configured (run 'aws configure')")
        console.print("2. kubectl not configured for your cluster")
        console.print("3. Insufficient permissions for Bedrock or EKS")
        return
    
    if test_only:
        console.print("🎉 Test completed successfully! You can now use the interactive mode.", style="green")
        return
    
    try:
        # Initialize agent
        console.print(f"🤖 Initializing agent with model: {model}", style="blue")
        agent = create_kubernetes_agent(model_name=model, region=region)
        
        # Show agent info
        agent_info = agent.get_agent_info()
        console.print(f"📊 Model: {agent_info['model_info']['model_id']}", style="dim")
        console.print(f"🌍 Region: {agent_info['region']}", style="dim")
        console.print()
        
        # Show examples
        print_examples()
        
        # Interactive loop
        console.print("💬 Start asking questions! (Type 'quit', 'exit', or 'help' for commands)", style="green")
        console.print()
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("[bold blue]Your question[/bold blue]")
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("👋 Goodbye!", style="green")
                    break
                elif user_input.lower() in ['help', 'h']:
                    print_examples()
                    continue
                elif user_input.lower() in ['clear', 'cls']:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print_welcome()
                    continue
                
                # Process query
                console.print("🤔 Thinking...", style="yellow")
                response = agent.query(user_input)
                
                # Display response
                console.print()
                response_panel = Panel(
                    response,
                    title="Response",
                    style="green"
                )
                console.print(response_panel)
                console.print()
                
            except KeyboardInterrupt:
                console.print("\n👋 Goodbye!", style="green")
                break
            except Exception as e:
                console.print(f"❌ Error: {e}", style="red")
                
    except Exception as e:
        console.print(f"❌ Failed to initialize agent: {e}", style="red")


@cli.command()
@click.argument('query')
@click.option('--model', default='claude-3-haiku',
              help='Bedrock model to use')
@click.option('--region', default=None,
              help='AWS region for Bedrock')
def query(query: str, model: str, region: Optional[str]):
    """Execute a single query and return the result."""
    
    try:
        # Initialize agent
        agent = create_kubernetes_agent(model_name=model, region=region)
        
        # Execute query
        response = agent.query(query)
        
        # Print response
        console.print(response)
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)


@cli.command()
def models():
    """List available Bedrock models."""
    
    available_models = BedrockLLM.list_available_models()
    
    table = Table(title="Available Bedrock Models")
    table.add_column("Model Name", style="cyan")
    table.add_column("Model ID", style="yellow")
    table.add_column("Max Tokens", style="green")
    table.add_column("Temperature", style="blue")
    
    for name, config in available_models.items():
        table.add_row(
            name,
            config["model_id"],
            str(config["max_tokens"]),
            str(config["temperature"])
        )
    
    console.print(table)


@cli.command()
def test():
    """Test the system configuration."""
    if test_setup():
        console.print("🎉 All tests passed! The system is ready to use.", style="green")
    else:
        console.print("❌ Some tests failed. Please check your configuration.", style="red")
        sys.exit(1)


if __name__ == '__main__':
    cli()
