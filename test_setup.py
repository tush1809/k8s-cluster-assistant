"""
Example usage and testing script for the Kubernetes cluster interface.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from k8s_client import KubernetesClient
from tools.k8s_tools import get_kubernetes_tools
from bedrock import create_bedrock_llm
from agent import create_kubernetes_agent


def test_k8s_client():
    """Test the Kubernetes client directly."""
    print("Testing Kubernetes Client...")
    
    try:
        client = KubernetesClient()
        
        # Test cluster info
        cluster_info = client.get_cluster_info()
        print(f"✅ Cluster Info: {cluster_info['total_namespaces']} namespaces, {cluster_info['total_pods']} pods")
        
        # Test namespaces
        namespaces = client.list_namespaces()
        print(f"✅ Namespaces: Found {len(namespaces)} namespaces")
        
        return True
        
    except Exception as e:
        print(f"❌ Kubernetes client error: {e}")
        return False


def test_bedrock_llm():
    """Test the Bedrock LLM connection."""
    print("Testing Bedrock LLM...")
    
    try:
        bedrock = create_bedrock_llm()
        
        # Test connection
        if bedrock.test_connection():
            print("✅ Bedrock connection successful")
            return True
        else:
            print("❌ Bedrock connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Bedrock error: {e}")
        return False


def test_tools():
    """Test the LangChain tools."""
    print("Testing LangChain Tools...")
    
    try:
        tools = get_kubernetes_tools()
        print(f"✅ Loaded {len(tools)} tools: {[tool.name for tool in tools]}")
        
        # Test one tool
        cluster_tool = next(tool for tool in tools if tool.name == "get_cluster_info")
        result = cluster_tool._run()
        print(f"✅ Tool test result: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Tools error: {e}")
        return False


def test_agent():
    """Test the complete agent."""
    print("Testing Complete Agent...")
    
    try:
        agent = create_kubernetes_agent()
        
        # Test simple query
        response = agent.query("What's the cluster overview?")
        print(f"✅ Agent response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Running Kubernetes Cluster Interface Tests\n")
    
    tests = [
        ("Kubernetes Client", test_k8s_client),
        ("Bedrock LLM", test_bedrock_llm),
        ("LangChain Tools", test_tools),
        ("Complete Agent", test_agent)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"Testing: {test_name}")
        print(f"{'='*50}")
        
        success = test_func()
        results.append((test_name, success))
        
        print(f"Result: {'✅ PASSED' if success else '❌ FAILED'}")
        print()
    
    # Summary
    print(f"{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:20}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
