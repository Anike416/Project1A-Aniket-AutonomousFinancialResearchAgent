#!/usr/bin/env python
"""
Setup script for ARA-1 agent
"""
import os
import sys
import subprocess
from pathlib import Path


def create_directories():
    """Create necessary directories"""
    dirs = [
        "logs",
        "data",
        "data/cache",
        "reports",
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {d}")


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("✓ Dependencies installed")


def setup_environment():
    """Setup environment configuration"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"\n⚠ {env_file} not found")
        print("Creating from template...")
        subprocess.run(["cp", ".env.example", env_file], check=False)
        print(f"✓ Created {env_file}")
        print(f"⚠ Please edit {env_file} with your credentials")
        return False
    else:
        print(f"✓ {env_file} exists")
        return True


def verify_aws_config():
    """Verify AWS configuration"""
    print("\nVerifying AWS configuration...")
    
    try:
        import boto3
        from src.config.settings import settings
        
        # Try to create Bedrock client
        client = boto3.client('bedrock-runtime', region_name=settings.aws_region)
        print("✓ AWS Bedrock client initialized")
        return True
    except Exception as e:
        print(f"⚠ AWS configuration error: {str(e)}")
        print("  Please verify your AWS credentials in .env file")
        return False


def initialize_agent():
    """Initialize the agent"""
    print("\nInitializing agent...")
    
    try:
        from src.agents.research_agent import get_agent
        from src.tools.base_tool import get_tool_registry
        from src.config.logger import setup_logging
        
        setup_logging()
        
        # Initialize tool registry
        registry = get_tool_registry()
        print(f"✓ Tool registry initialized with {len(registry.list_tools())} tools")
        
        # Initialize agent
        agent = get_agent()
        print("✓ Agent initialized successfully")
        
        return True
    except Exception as e:
        print(f"⚠ Error initializing agent: {str(e)}")
        return False


def main():
    """Main setup routine"""
    print("=" * 60)
    print("ARA-1 Agent Setup")
    print("=" * 60)
    
    try:
        # Step 1: Create directories
        create_directories()
        
        # Step 2: Install dependencies
        install_dependencies()
        
        # Step 3: Setup environment
        env_ok = setup_environment()
        
        if not env_ok:
            print("\n⚠ Setup incomplete - please configure .env file and run setup again")
            return 1
        
        # Step 4: Verify AWS
        if not verify_aws_config():
            print("\n⚠ AWS configuration issues detected")
            print("  The agent may not function without proper AWS credentials")
        
        # Step 5: Initialize agent
        if initialize_agent():
            print("\n" + "=" * 60)
            print("✓ Setup completed successfully!")
            print("=" * 60)
            print("\nYou can now run:")
            print("  python -m src.main init")
            print("  python -m src.main research 'Your research query'")
            print("  python -m src.main evaluate")
            print("  python -m src.main interactive")
            return 0
        else:
            print("\n⚠ Setup completed with issues")
            return 1
            
    except Exception as e:
        print(f"\n✗ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
