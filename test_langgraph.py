#!/usr/bin/env python3
"""
Test script for the LangGraph-based Kubernetes agent.
This will test the agent without requiring AWS credentials.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import create_kubernetes_agent
from bedrock import BedrockLLM
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_langgraph_agent():
    """Test the LangGraph agent with mock mode."""
    print("🚀 Testing LangGraph Kubernetes Agent")
    print("=" * 50)
    
    try:
        # Test with mock mode
        print("\n1. Testing agent initialization with mock mode...")
        os.environ['MOCK_MODE'] = 'true'
        
        # Create agent
        agent = create_kubernetes_agent()
        print("✅ Agent created successfully!")
        
        # Test tools directly first
        print("\n2. Testing tools directly...")
        from tools.simple_tools import AVAILABLE_TOOLS, initialize_k8s_client
        
        initialize_k8s_client()
        
        for tool_name, tool_info in AVAILABLE_TOOLS.items():
            try:
                print(f"   Testing {tool_name}...")
                result = tool_info["function"]()
                if result:
                    print(f"   ✅ {tool_name} works!")
                else:
                    print(f"   ⚠️  {tool_name} returned empty result")
            except Exception as e:
                print(f"   ❌ {tool_name} failed: {e}")
        
        # Test simple queries
        print("\n3. Testing agent queries...")
        test_queries = [
            "What's the cluster overview?",
            "List all namespaces",
            "How many pods are running?"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            try:
                response = agent.query(query)
                print(f"   Response: {response[:100]}...")
                print("   ✅ Query processed successfully!")
            except Exception as e:
                print(f"   ❌ Query failed: {e}")
        
        print("\n4. Testing agent commands...")
        commands = agent.get_available_commands()
        print(f"   Available commands: {len(commands)} examples")
        for i, cmd in enumerate(commands[:3]):
            print(f"   {i+1}. {cmd}")
        
        print("\n🎉 All tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_langgraph_agent()
    sys.exit(0 if success else 1)
