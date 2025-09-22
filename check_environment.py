"""
Simple script to check Python environment and dependencies.
Run this to see what's installed and what needs to be installed.
"""

import sys
import subprocess
import importlib.util

def check_python():
    """Check Python version."""
    print(f"🐍 Python version: {sys.version}")
    print(f"📍 Python executable: {sys.executable}")
    print()

def check_package(package_name):
    """Check if a package is installed."""
    spec = importlib.util.find_spec(package_name)
    if spec is not None:
        try:
            module = importlib.import_module(package_name)
            version = getattr(module, '__version__', 'Unknown version')
            return f"✅ {package_name}: {version}"
        except ImportError:
            return f"⚠️  {package_name}: Found but can't import"
    else:
        return f"❌ {package_name}: Not installed"

def main():
    """Main function to check environment."""
    print("🔍 Kubernetes Cluster Interface - Environment Check")
    print("=" * 60)
    
    # Check Python
    check_python()
    
    # Required packages
    packages = [
        'boto3',
        'kubernetes',
        'langchain',
        'langchain_aws',
        'langchain_community', 
        'pydantic',
        'dotenv',
        'yaml',
        'click',
        'rich',
        'tabulate',
        'flask',
        'flask_cors'
    ]
    
    print("📦 Package Status:")
    print("-" * 40)
    
    installed = 0
    total = len(packages)
    
    for package in packages:
        status = check_package(package)
        print(status)
        if "✅" in status:
            installed += 1
    
    print()
    print(f"📊 Summary: {installed}/{total} packages installed")
    
    if installed == total:
        print("🎉 All dependencies are installed! You can start the web interface.")
        print("   Run: python start_web.py")
    else:
        print("⚠️  Missing dependencies. Install with:")
        print("   pip install -r requirements.txt")
    
    print()
    print("🌐 Web interface will be available at: http://localhost:5000")

if __name__ == "__main__":
    main()
