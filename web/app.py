"""
Web frontend for the Kubernetes cluster information interface.
Flask-based web application with a modern UI.
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import sys
import logging
from datetime import datetime
import json
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import create_kubernetes_agent
from bedrock import BedrockLLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# Global agent instance
agent = None


def initialize_agent():
    """Initialize the Kubernetes agent."""
    global agent
    try:
        model_name = os.getenv('BEDROCK_MODEL_NAME', 'claude-3-haiku')
        region = os.getenv('AWS_REGION', 'us-west-2')
        agent = create_kubernetes_agent(model_name=model_name, region=region)
        logger.info("Agent initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        return False


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    global agent
    
    if agent is None:
        success = initialize_agent()
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Agent initialization failed'
            }), 500
    
    try:
        # Test agent
        test_response = agent.query("What's the cluster overview?")
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'agent_ready': True
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'agent_ready': False
        }), 500


@app.route('/api/query', methods=['POST'])
def query_cluster():
    """Process natural language queries about the cluster."""
    global agent
    
    if agent is None:
        success = initialize_agent()
        if not success:
            return jsonify({
                'error': 'Agent not initialized',
                'message': 'Please check your AWS and Kubernetes configuration'
            }), 500
    
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
        
        user_query = data['query'].strip()
        if not user_query:
            return jsonify({'error': 'Empty query'}), 400
        
        logger.info(f"Processing query: {user_query}")
        
        # Process the query
        response = agent.query(user_query)
        
        # Store in session history
        if 'query_history' not in session:
            session['query_history'] = []
        
        session['query_history'].append({
            'query': user_query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 queries
        session['query_history'] = session['query_history'][-10:]
        
        return jsonify({
            'query': user_query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({
            'error': 'Query processing failed',
            'message': str(e)
        }), 500


@app.route('/api/examples')
def get_examples():
    """Get example queries users can try."""
    examples = [
        {
            'category': 'General',
            'queries': [
                "What's the cluster overview?",
                "How is my cluster doing?",
                "Give me a summary of the cluster"
            ]
        },
        {
            'category': 'Pods',
            'queries': [
                "How many pods are running?",
                "Show me pods in the default namespace",
                "Are there any failed pods?",
                "List all running pods"
            ]
        },
        {
            'category': 'Nodes',
            'queries': [
                "List all nodes",
                "How many nodes are ready?",
                "What's the node status?",
                "Show me node information"
            ]
        },
        {
            'category': 'Namespaces',
            'queries': [
                "List all namespaces",
                "What namespaces exist?",
                "Show me the namespaces"
            ]
        },
        {
            'category': 'Services',
            'queries': [
                "Show me all services",
                "List services in kube-system namespace",
                "What services are exposed?"
            ]
        }
    ]
    
    return jsonify(examples)


@app.route('/api/history')
def get_history():
    """Get query history for the current session."""
    history = session.get('query_history', [])
    return jsonify(history)


@app.route('/api/agent-info')
def get_agent_info():
    """Get information about the agent configuration."""
    global agent
    
    if agent is None:
        return jsonify({'error': 'Agent not initialized'}), 500
    
    try:
        agent_info = agent.get_agent_info()
        return jsonify(agent_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/models')
def get_available_models():
    """Get available Bedrock models."""
    try:
        models = BedrockLLM.list_available_models()
        return jsonify(models)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Initialize agent on startup
    print("🚀 Starting Kubernetes Cluster Information Web Interface")
    print("🤖 Initializing agent...")
    
    if initialize_agent():
        print("✅ Agent initialized successfully")
        print("🌐 Starting web server...")
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        )
    else:
        print("❌ Failed to initialize agent. Please check your configuration.")
        sys.exit(1)
