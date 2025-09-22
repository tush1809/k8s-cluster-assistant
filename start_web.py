"""
Web interface launcher script.
Simple script to start the Flask web application.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the web interface."""
    # Get the project root directory
    project_root = Path(__file__).parent
    web_dir = project_root / "web"
    
    # Change to web directory
    os.chdir(web_dir)
    
    # Add project root to Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    print("🚀 Starting Kubernetes Cluster Information Web Interface")
    print("📂 Project directory:", project_root)
    print("🌐 Web directory:", web_dir)
    print("🔗 Interface will be available at: http://localhost:5000")
    print()
    
    try:
        # Run the Flask app
        from web.app import app, initialize_agent
        
        # Initialize agent first
        print("🤖 Initializing Kubernetes agent...")
        if initialize_agent():
            print("✅ Agent initialized successfully")
            print("🌐 Starting web server...")
            print("📱 Open your browser and navigate to: http://localhost:5000")
            print("⏹️  Press Ctrl+C to stop the server")
            print()
            
            app.run(
                host='0.0.0.0',
                port=5000,
                debug=False
            )
        else:
            print("❌ Failed to initialize agent")
            print("Please check your AWS and Kubernetes configuration")
            return 1
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped")
        return 0
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
